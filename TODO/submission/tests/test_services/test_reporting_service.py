import unittest
from unittest.mock import MagicMock, call
import datetime

# Import the class we are testing
from submission.services.reporting_service import ReportingService

# Import the Enum for status checks
from submission.domain.enums.order_status import OrderStatus

# We will use MagicMock for all dependencies and models

class TestReportingService(unittest.TestCase):

    def setUp(self):
        """
        Set up a fresh service and mock dependencies for each test.
        """
        self.mock_data_store = MagicMock()
        self.mock_customer_service = MagicMock()
        
        self.reporting_service = ReportingService(
            data_store=self.mock_data_store,
            customer_service=self.mock_customer_service
        )
        
        # Define a standard date range for tests
        self.start_date = datetime.datetime(2023, 1, 1)
        self.end_date = datetime.datetime(2023, 1, 31)

    def test_generate_sales_report_comprehensive(self):
        """
        Tests that the report correctly aggregates data from multiple
        orders, products, and customers within the date range.
        """
        # 1. Arrange
        
        # --- Mock Products ---
        prod_A = MagicMock(product_id="P1", category="Electronics")
        prod_B = MagicMock(product_id="P2", category="Books")
        
        # --- Mock Order Items ---
        item_A1 = MagicMock(product_id="P1", quantity=2, unit_price=100.0) # 200.0
        item_B1 = MagicMock(product_id="P2", quantity=1, unit_price=20.0)  # 20.0
        item_B2 = MagicMock(product_id="P2", quantity=3, unit_price=20.0)  # 60.0

        # --- Mock Orders ---
        order_1_in_range = MagicMock(
            created_at=datetime.datetime(2023, 1, 5),
            status=OrderStatus.SHIPPED,  # <-- FIX: Was COMPLETED
            total_price=220.0,
            items=[item_A1, item_B1]
        )
        order_2_in_range = MagicMock(
            created_at=datetime.datetime(2023, 1, 10),
            status=OrderStatus.SHIPPED,
            total_price=60.0,
            items=[item_B2]
        )
        order_3_cancelled = MagicMock(
            created_at=datetime.datetime(2023, 1, 15),
            status=OrderStatus.CANCELLED,
            total_price=100.0,
            items=[]
        )
        order_4_out_of_range = MagicMock(
            created_at=datetime.datetime(2023, 2, 1),
            status=OrderStatus.DELIVERED, # <-- Also valid
            total_price=50.0,
            items=[]
        )
        
        # --- Mock DataStore (Orders) ---
        self.mock_data_store.orders.values.return_value = [
            order_1_in_range, 
            order_2_in_range, 
            order_3_cancelled, 
            order_4_out_of_range
        ]
        
        # --- Mock DataStore (Products) ---
        def get_product_side_effect(product_id):
            if product_id == "P1": return prod_A
            if product_id == "P2": return prod_B
            return None
        self.mock_data_store.get_product.side_effect = get_product_side_effect
        
        # --- Mock CustomerService (LTV) ---
        self.mock_data_store.customers.keys.return_value = ["C1", "C2", "C3"]
        def get_ltv_side_effect(customer_id):
            if customer_id == "C1": return 500.0
            if customer_id == "C2": return 1000.0
            if customer_id == "C3": return 200.0
            return 0.0
        self.mock_customer_service.get_customer_lifetime_value.side_effect = get_ltv_side_effect

        # 2. Act
        report = self.reporting_service.generate_sales_report(self.start_date, self.end_date)

        # 3. Assert
        
        # Check sales and order counts
        self.assertEqual(report['total_sales'], 280.0) # 220.0 (Order 1) + 60.0 (Order 2)
        self.assertEqual(report['total_orders'], 2)
        self.assertEqual(report['cancelled_orders'], 1)
        
        # Check product tally
        self.assertEqual(report['products_sold'], {"P1": 2, "P2": 4})
        
        # Check category revenue
        self.assertEqual(report['revenue_by_category'], {"Electronics": 200.0, "Books": 80.0})
        
        # Check top customers (should be sorted by LTV)
        expected_top_customers = [("C2", 1000.0), ("C1", 500.0), ("C3", 200.0)]
        self.assertEqual(report['top_customers'], expected_top_customers)

    def test_generate_sales_report_empty_state(self):
        """
        Tests that a default (zeroed-out) report is returned if no data exists.
        """
        # 1. Arrange
        self.mock_data_store.orders.values.return_value = []
        self.mock_data_store.customers.keys.return_value = []
        
        # 2. Act
        report = self.reporting_service.generate_sales_report(self.start_date, self.end_date)
        
        # 3. Assert
        self.assertEqual(report['total_sales'], 0.0)
        self.assertEqual(report['total_orders'], 0)
        self.assertEqual(report['cancelled_orders'], 0)
        self.assertEqual(report['products_sold'], {})
        self.assertEqual(report['revenue_by_category'], {})
        self.assertEqual(report['top_customers'], [])

    def test_generate_sales_report_with_missing_product(self):
        """
        Tests that the report handles an order item for a product
        that no longer exists in the datastore.
        """
        # 1. Arrange
        
        # --- Mock Order Items ---
        item_A = MagicMock(product_id="P1", quantity=2, unit_price=100.0)
        item_BAD = MagicMock(product_id="P_BAD", quantity=5, unit_price=10.0)

        # --- Mock Orders ---
        order_1 = MagicMock(
            created_at=datetime.datetime(2023, 1, 5),
            status=OrderStatus.SHIPPED,  # <-- FIX: Was COMPLETED
            total_price=250.0, # 200 + 50
            items=[item_A, item_BAD]
        )
        
        # --- Mock DataStore (Orders) ---
        self.mock_data_store.orders.values.return_value = [order_1]
        
        # --- Mock DataStore (Products) ---
        prod_A = MagicMock(product_id="P1", category="Electronics")
        self.mock_data_store.get_product.side_effect = lambda pid: prod_A if pid == "P1" else None
        
        # --- Mock CustomerService ---
        self.mock_data_store.customers.keys.return_value = []

        # 2. Act
        report = self.reporting_service.generate_sales_report(self.start_date, self.end_date)

        # 3. Assert
        self.assertEqual(report['total_sales'], 250.0)
        self.assertEqual(report['total_orders'], 1)
        self.mock_data_store.get_product.assert_has_calls([call("P1"), call("P_BAD")])
        self.assertEqual(report['products_sold'], {"P1": 2})
        self.assertEqual(report['revenue_by_category'], {"Electronics": 200.0})
