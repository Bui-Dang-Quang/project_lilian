import unittest
import datetime
from submission.domain.models.Customer import Customer
from submission.domain.models.Order import Order
from submission.domain.models.OrderItem import OrderItem 
from submission.domain.models.Supplier import Supplier
from submission.domain.models.Promotion import Promotion
from submission.domain.models.Product import Product
from submission.domain.enums.order_status import OrderStatus
from submission.services.pricing.strategies.membership_discount import GoldMembership, BronzeMembership, SilverMembership, SuspendedMembership

class TestProductModel(unittest.TestCase):
    def test_product_creation(self):
        product = Product("p1", "Laptop", 999.99, 10, "Elec", 2.5, "s1")
        self.assertEqual(product.product_id, "p1")
        self.assertEqual(product.name, "Laptop")
        self.assertEqual(product.price, 999.99)
        self.assertEqual(product.quantity_available, 10)
        self.assertEqual(product.category, "Elec")
        self.assertEqual(product.weight, 2.5)
        self.assertEqual(product.supplier_id, "s1")
        self.assertTrue(product.discount_eligible)

class TestCustomerModel(unittest.TestCase):
    def test_customer_Gold_creation(self):
        customer = Customer("c1", "Alice", "a@b.com", "gold", "555", "123 St", 100)
        self.assertEqual(customer.customer_id, "c1")
        self.assertEqual(customer.name, "Alice")
        self.assertEqual(customer.email, "a@b.com")
        self.assertEqual(customer.phone, "555")
        self.assertEqual(customer.address, "123 St")
        self.assertEqual(customer.loyalty_points, 100)
        self.assertIsInstance(customer.membership_tier, GoldMembership)
        self.assertEqual(customer.order_history, [])
    
    def test_customer_Silver_creation(self):
        customer = Customer("c1", "Alice", "a@b.com", "silver", "555", "123 St", 100)
        self.assertEqual(customer.customer_id, "c1")
        self.assertEqual(customer.name, "Alice")
        self.assertEqual(customer.email, "a@b.com")
        self.assertEqual(customer.phone, "555")
        self.assertEqual(customer.address, "123 St")
        self.assertEqual(customer.loyalty_points, 100)
        self.assertIsInstance(customer.membership_tier, SilverMembership)
        self.assertEqual(customer.order_history, [])
    
    def test_customer_Bronze_creation(self):
        customer = Customer("c1", "Alice", "a@b.com", "bronze", "555", "123 St", 100)
        self.assertEqual(customer.customer_id, "c1")
        self.assertEqual(customer.name, "Alice")
        self.assertEqual(customer.email, "a@b.com")
        self.assertEqual(customer.phone, "555")
        self.assertEqual(customer.address, "123 St")
        self.assertEqual(customer.loyalty_points, 100)
        self.assertIsInstance(customer.membership_tier, BronzeMembership)
        self.assertEqual(customer.order_history, [])
        
    def test_customer_Suspended_creation(self):
        customer = Customer("c1", "Alice", "a@b.com", "suspended", "555", "123 St", 100)
        self.assertEqual(customer.customer_id, "c1")
        self.assertEqual(customer.name, "Alice")
        self.assertEqual(customer.email, "a@b.com")
        self.assertEqual(customer.phone, "555")
        self.assertEqual(customer.address, "123 St")
        self.assertEqual(customer.loyalty_points, 100)
        self.assertIsInstance(customer.membership_tier, SuspendedMembership)
        self.assertEqual(customer.order_history, [])

class TestOrderItemModel(unittest.TestCase):
    def test_order_item_creation(self):
        item = OrderItem("p1", 2, 50.00)
        self.assertEqual(item.product_id, "p1")
        self.assertEqual(item.quantity, 2)
        self.assertEqual(item.unit_price, 50.00)
        self.assertEqual(item.discount_applied, 0.0)

class TestOrderModel(unittest.TestCase):
    def test_order_creation(self):
        item = OrderItem("p1", 1, 100.00)
        now = datetime.datetime.now()
        order = Order(1, "c1", [item], OrderStatus.PENDING, now, 110.00, 10.00)
        
        self.assertEqual(order.order_id, 1)
        self.assertEqual(order.customer_id, "c1")
        self.assertEqual(order.items[0], item)
        self.assertEqual(order.status, OrderStatus.PENDING)
        self.assertEqual(order.created_at, now)
        self.assertEqual(order.total_price, 110.00)
        self.assertEqual(order.shipping_cost, 10.00)
        self.assertIsNone(order.tracking_number)
        self.assertIsNone(order.payment_method)

class TestSupplierModel(unittest.TestCase):
    def test_supplier_creation(self):
        supplier = Supplier("s1", "Supplier Inc", "s@s.com", 4.5)
        self.assertEqual(supplier.supplier_id, "s1")
        self.assertEqual(supplier.name, "Supplier Inc")
        self.assertEqual(supplier.email, "s@s.com")
        self.assertEqual(supplier.reliability_score, 4.5)

class TestPromotionModel(unittest.TestCase):
    def test_promotion_creation(self):
        now = datetime.datetime.now()
        promo = Promotion("promo1", "CODE", 10.0, 50.0, now, "all")
        self.assertEqual(promo.promo_id, "promo1")
        self.assertEqual(promo.code, "CODE")
        self.assertEqual(promo.discount_percent, 10.0)
        self.assertEqual(promo.min_purchase, 50.0)
        self.assertEqual(promo.valid_until, now)
        self.assertEqual(promo.category, "all")
        self.assertEqual(promo.used_count, 0)
