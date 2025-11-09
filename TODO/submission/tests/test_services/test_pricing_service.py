import unittest
import datetime
import io  # <-- Import io for capturing stdout
from unittest.mock import Mock, MagicMock, patch  # <-- Import patch

# --- Import the class we are testing ---
from submission.services.pricing.PricingService import PricingService

# --- Import dependencies needed for tests ---
from submission.domain.models.OrderItem import OrderItem
from submission.services.pricing.strategies.bulk_discount import (
    BulkDiscount,
    NoBulkDiscount,
    FiveItemsDiscount,
    TenItemsDiscount
)

class TestPricingServiceWithMocks(unittest.TestCase):
    
    def setUp(self):
        """Set up a fresh environment for each test."""
        
        self.bulk_strategies = [NoBulkDiscount(), FiveItemsDiscount(), TenItemsDiscount()]

        self.customer_gold = Mock()
        self.customer_gold.membership_tier.get_discount.return_value = 0.20
        self.customer_gold.loyalty_points = 0

        self.customer_loyal = Mock()
        self.customer_loyal.membership_tier.get_discount.return_value = 0.0
        self.customer_loyal.loyalty_points = 500

        self.customer_normal = Mock()
        self.customer_normal.membership_tier.get_discount.return_value = 0.0
        self.customer_normal.loyalty_points = 50 

        self.store = MagicMock()
        
        product1 = Mock(product_id="p1", category="electronics", price=100.0)
        product2 = Mock(product_id="p2", category="books", price=50.0)
        self.store.get_product.side_effect = lambda pid: {"p1": product1, "p2": product2}.get(pid)

        valid_promo = Mock(
            code="VALID10", discount_percent=10, min_purchase=50, category="all",
            valid_until=datetime.datetime.now() + datetime.timedelta(days=30),
            used_count=0
        )
        expired_promo = Mock(
            code="EXPIRED", discount_percent=50, min_purchase=0, category="all",
            valid_until=datetime.datetime.now() - datetime.timedelta(days=1),
            used_count=0
        )
        min_promo = Mock(
            code="MIN_PURCHASE", discount_percent=10, min_purchase=500, category="all",
            valid_until=datetime.datetime.now() + datetime.timedelta(days=30),
            used_count=0
        )
        books_promo = Mock(
            code="BOOKS_ONLY", discount_percent=20, min_purchase=0, category="books",
            valid_until=datetime.datetime.now() + datetime.timedelta(days=30),
            used_count=0
        )
        
        self.store.promotions.get.side_effect = lambda code: {
            "VALID10": valid_promo,
            "EXPIRED": expired_promo,
            "MIN_PURCHASE": min_promo,
            "BOOKS_ONLY": books_promo
        }.get(code)

    # --- Test Methods ---

    def test_apply_membership_discount(self):
        items = [OrderItem("p1", 1, 100.0)]
        service = PricingService(items, self.store)
        service.apply_membership_discount(self.customer_gold)
        self.assertAlmostEqual(service.discounted_price, 80.0)
        self.assertEqual(service.membership_discount_amount, 20.0)

    def test_apply_loyalty_discount_success(self):
        items = [OrderItem("p1", 1, 100.0)]
        service = PricingService(items, self.store)
        service.apply_loyalty_discount(self.customer_loyal)
        self.assertAlmostEqual(service.discounted_price, 95.0)
        self.assertEqual(service.loyalty_discount_amount, 5.0)
        self.assertEqual(self.customer_loyal.loyalty_points, 0)

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_apply_loyalty_fail_not_enough_points(self, mock_stdout):
        """Test loyalty discount failure (line 130)."""
        items = [OrderItem("p1", 1, 100.0)]
        service = PricingService(items, self.store)
        
        service.apply_loyalty_discount(self.customer_normal) # 50 points
        
        self.assertAlmostEqual(service.discounted_price, 100.0)
        self.assertEqual(service.loyalty_discount_amount, 0.0)
        self.assertEqual(
            mock_stdout.getvalue().strip(), 
            "Not enough loyalty points to apply discount."
        )

    def test_apply_bulk_discount_no_discount(self):
        items = [OrderItem("p1", 4, 10.0)]
        service = PricingService(items, self.store)
        service.apply_bulk_discount(self.bulk_strategies)
        self.assertAlmostEqual(service.discounted_price, 40.0)
        self.assertEqual(service.bulk_discount_amount, 0.0)

    def test_apply_bulk_discount_5_items(self):
        items = [OrderItem("p1", 6, 10.0)]
        service = PricingService(items, self.store)
        service.apply_bulk_discount(self.bulk_strategies)
        self.assertAlmostEqual(service.discounted_price, 58.8)
        self.assertEqual(service.bulk_discount_amount, 1.2)

    def test_apply_bulk_discount_10_items_chooses_best(self):
        items = [OrderItem("p1", 11, 10.0)]
        service = PricingService(items, self.store)
        service.apply_bulk_discount(self.bulk_strategies)
        self.assertAlmostEqual(service.discounted_price, 104.5)
        self.assertEqual(service.bulk_discount_amount, 5.5)

    def test_promotion_success_all_category(self):
        items = [OrderItem("p1", 1, 100.0)]
        service = PricingService(items, self.store)
        service.apply_promotion_discount("VALID10")
        self.assertAlmostEqual(service.discounted_price, 90.0)
        self.assertEqual(service.promotion_discount_amount, 10.0)

    def test_promotion_success_specific_category(self):
        items = [OrderItem("p2", 2, 50.0)]
        service = PricingService(items, self.store)
        service.apply_promotion_discount("BOOKS_ONLY")
        self.assertAlmostEqual(service.discounted_price, 80.0)
        self.assertEqual(service.promotion_discount_amount, 20.0)
    
    def test_promotion_failures_all_cases(self):
        items = [OrderItem("p1", 1, 100.0)]
        service = PricingService(items, self.store)
        
        service.apply_promotion_discount("EXPIRED")
        self.assertAlmostEqual(service.discounted_price, 100.0)
        
        service.apply_promotion_discount(None)
        self.assertAlmostEqual(service.discounted_price, 100.0)

        service.apply_promotion_discount("MIN_PURCHASE")
        self.assertAlmostEqual(service.discounted_price, 100.0)
        
        service.apply_promotion_discount("BOOKS_ONLY")
        self.assertAlmostEqual(service.discounted_price, 100.0)

        service.apply_promotion_discount("FAKECODE")
        self.assertAlmostEqual(service.discounted_price, 100.0)

    # --- ADDED TEST ---
    def test_get_final_discounted_price(self):
        """Tests that the getter method returns the correct value."""
        items = [OrderItem("p1", 1, 100.0)]
        service = PricingService(items, self.store)
        
        # Manually set the price to test the getter
        service.discounted_price = 77.77
        
        self.assertEqual(service.get_final_discounted_price(), 77.77)
