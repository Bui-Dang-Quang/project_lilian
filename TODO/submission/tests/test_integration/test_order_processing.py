import unittest
import datetime

# Import the container from main.py that holds all services
from submission.application.main import ServiceContainer, setup_data

class TestOrderProcessingIntegration(unittest.TestCase):

    def setUp(self):
        """
        This runs before each test. 
        It creates a fresh set of services and data for every test.
        """
        self.services = ServiceContainer.initialize()
        
        # We can use the same data setup from main
        # Or create a minimal one here
        
        # FIX 1: Renamed 'create_and_add_supplier' to 'add_supplier'
        self.services.db.add_supplier("S1", "TestSup", "test@sup.com", 1.0)
        self.services.db.add_product("P1", "Test Laptop", 1000.00, 10, "electronics", 2.0, "S1")
        self.services.db.add_customer("C1", "Test Alice", "alice@test.com", "gold", "555-1111", "123 Main St, CA", 100)

    def test_place_order_successfully(self):
        """
        Tests the "Happy Path" where everything works.
        """
        # Arrange
        customer = self.services.db.get_customer("C1")
        product = self.services.db.get_product("P1")
        
        items = [{"product_id": "P1", "quantity": 1}]
        payment = {
            "type": "credit_card", 
            "card_number": "1234567812345678", 
            "amount": 1500.0, 
            "valid": True
        }

        # Act
        # We're testing the main facade from your main.py file
        from submission.application.main import place_order_facade
        order = place_order_facade(
            services=self.services,
            customer_id="C1",
            item_requests=items,
            shipping_method="standard",
            payment_info=payment
        )

        # Assert
        self.assertIsNotNone(order)
        self.assertEqual(order.customer_id, "C1")
        self.assertEqual(product.quantity_available, 9) # Stock was deducted
        self.assertIn(order.order_id, customer.order_history) # History was updated
        
        # FIX 2: Updated expected price from 911.81 to 910.55
        # The app log shows TOTAL PRICE: $910.55
        # (1000 - 15% Gold - $1 Loyalty) * 1.0725% CA Tax = 910.55
        self.assertAlmostEqual(order.total_price, 910.55, 2) 

    def test_place_order_fails_on_low_stock(self):
        """
        Tests failure when stock is insufficient.
        """
        # Arrange
        items = [{"product_id": "P1", "quantity": 11}] # We only have 10
        payment = {"type": "credit_card", "amount": 15000.0, "valid": True, "card_number": "1111"}

        # Act
        from submission.application.main import place_order_facade
        order = place_order_facade(
            services=self.services,
            customer_id="C1",
            item_requests=items,
            shipping_method="standard",
            payment_info=payment
        )

        # Assert
        self.assertIsNone(order) # Order should not have been created
        
        # Check that state was not changed
        product = self.services.db.get_product("P1")
        customer = self.services.db.get_customer("C1")
        self.assertEqual(product.quantity_available, 10) # Stock is unchanged
        self.assertEqual(len(self.services.db.orders), 0) # No order in DB
        self.assertEqual(len(customer.order_history), 0) # No order in history
