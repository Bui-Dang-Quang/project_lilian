import unittest
import datetime
from submission.repositories.in_memory.DataStore import DataStore
from submission.domain.models.Product import Product
from submission.domain.models.Customer import Customer

class TestDataStore(unittest.TestCase):
    
    def setUp(self):
        """Set up a fresh DataStore before each test."""
        self.store = DataStore()
    
    def test_initial_state(self):
        self.assertEqual(self.store.products, {})
        self.assertEqual(self.store.customers, {})
        self.assertEqual(self.store.orders, {})
        self.assertEqual(self.store.next_order_id, 1)
        self.assertEqual(self.store.next_shipment_id, 1)

    def test_add_product(self):
        self.store.add_product("p1", "Laptop", 999.99, 10, "Elec", 2.5, "s1")
        
        # Check if product was added to dictionary
        self.assertIn("p1", self.store.products)
        
        # Check if get_product works
        product = self.store.get_product("p1")
        self.assertIsNotNone(product)
        self.assertEqual(product.name, "Laptop")
        self.assertEqual(product.quantity_available, 10)
        
        # Check if inventory was logged
        self.assertEqual(len(self.store.inventory_logs), 1)
        log = self.store.inventory_logs[0]
        self.assertEqual(log['product_id'], "p1")
        self.assertEqual(log['quantity_change'], 10)
        self.assertEqual(log['reason'], "initial_stock")

    def test_get_product_not_found(self):
        product = self.store.get_product("nonexistent")
        self.assertIsNone(product)

    def test_add_customer(self):
        self.store.add_customer("c1", "Alice", "a@b.com", "gold", "555", "123 St", 100)
        
        # Check if customer was added
        self.assertIn("c1", self.store.customers)
        
        # Check if get_customer works
        customer = self.store.get_customer("c1")
        self.assertIsNotNone(customer)
        self.assertEqual(customer.name, "Alice")
        self.assertEqual(customer.loyalty_points, 100)
        self.assertEqual(customer.membership_tier.get_name(), "gold")
        
    def test_get_customer_not_found(self):
        customer = self.store.get_customer("nonexistent")
        self.assertIsNone(customer)

    def test_add_supplier(self):
        self.store.add_supplier("s1", "Supplier Inc", "s@s.com", 4.5)
        self.assertIn("s1", self.store.suppliers)
        supplier = self.store.get_supplier("s1")
        self.assertIsNotNone(supplier)
        self.assertEqual(supplier.name, "Supplier Inc")

    def test_add_promotion(self):
        now = datetime.datetime.now()
        self.store.add_promotion("promo1", "CODE10", 10.0, 50.0, now, "all")
        self.assertIn("CODE10", self.store.promotions)
        promo = self.store.promotions.get("CODE10")
        self.assertIsNotNone(promo)
        self.assertEqual(promo.discount_percent, 10.0)

# if __name__ == "__main__":
#     unittest.main(argv=['first-arg-is-ignored'], exit=False)
