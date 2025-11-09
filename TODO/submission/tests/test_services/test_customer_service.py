import unittest
from unittest.mock import MagicMock, patch, call
import io
import datetime # Import the real datetime module

# Import the class we are testing
from submission.services.customer_service import CustomerService

# Import the membership classes to check types during upgrades
from submission.services.pricing.strategies.membership_discount import (
    BronzeMembership,
    SilverMembership,
    GoldMembership,
    SuspendedMembership
)

class TestCustomerService(unittest.TestCase):

    def setUp(self):
        """
        Set up a fresh service and mock DataStore for each test.
        """
        self.mock_data_store = MagicMock()
        self.customer_service = CustomerService(data_store=self.mock_data_store)

    def test_finalize_customer_order_updates(self):
        """
        Tests that customer's order history and loyalty points are updated.
        """
        # 1. Arrange
        mock_customer = MagicMock()
        mock_customer.order_history = []
        mock_customer.loyalty_points = 100
        
        # 2. Act
        self.customer_service.finalize_customer_order_updates(
            mock_customer, 
            order_id=9001, 
            subtotal=120.50
        )

        # 3. Assert
        self.assertEqual(mock_customer.order_history, [9001])
        self.assertEqual(mock_customer.loyalty_points, 220)

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_refund_loyalty_points_for_order(self, mock_stdout):
        """
        Tests that the placeholder refund message is printed correctly.
        """
        # 1. Arrange
        mock_customer = MagicMock()
        mock_customer.name = "John Doe"
        mock_order = MagicMock()
        mock_order.order_id = 700
        
        # 2. Act
        self.customer_service.refund_loyalty_points_for_order(mock_customer, mock_order)
        
        # 3. Assert
        expected_output = "Processing loyalty point refund for John Doe for order 700.\n"
        self.assertEqual(mock_stdout.getvalue(), expected_output)

    def test_get_customer_lifetime_value_customer_not_found(self):
        """
        Tests that LTV is 0.0 if the customer is not found.
        (Covers line 103)
        """
        # 1. Arrange
        self.mock_data_store.get_customer.return_value = None
        
        # 2. Act
        ltv = self.customer_service.get_customer_lifetime_value("C_BAD_ID")
        
        # 3. Assert
        self.assertEqual(ltv, 0.0)
        self.mock_data_store.get_customer.assert_called_once_with("C_BAD_ID")

    def test_get_customer_lifetime_value_calculates_correctly(self):
        """
        Tests that LTV is calculated correctly, summing non-cancelled orders.
        """
        # 1. Arrange
        order1_completed = MagicMock(total_price=100.0, status='completed')
        order2_cancelled = MagicMock(total_price=50.0, status='cancelled')
        order3_processing = MagicMock(total_price=200.0, status='processing')
        
        mock_customer = MagicMock()
        mock_customer.order_history = [1, 2, 3]
        
        self.mock_data_store.get_customer.return_value = mock_customer
        
        def get_order_side_effect(order_id):
            if order_id == 1: return order1_completed
            if order_id == 2: return order2_cancelled
            if order_id == 3: return order3_processing
            return None
        
        self.mock_data_store.orders.get.side_effect = get_order_side_effect

        # 2. Act
        ltv = self.customer_service.get_customer_lifetime_value("C1")

        # 3. Assert
        self.assertEqual(ltv, 300.0)
        self.mock_data_store.get_customer.assert_called_once_with("C1")
        self.mock_data_store.orders.get.assert_has_calls([call(1), call(2), call(3)])

    def test_get_customer_lifetime_value_with_missing_order(self):
        """
        Tests LTV calculation when an order in history is not found.
        (Covers line 112 'if order:')
        """
        # 1. Arrange
        order1 = MagicMock(total_price=100.0, status='completed')
        
        mock_customer = MagicMock()
        mock_customer.order_history = [1, 99] # Order 99 does not exist
        
        self.mock_data_store.get_customer.return_value = mock_customer
        
        def get_order_side_effect(order_id):
            if order_id == 1: return order1
            return None # Return None for order 99
        
        self.mock_data_store.orders.get.side_effect = get_order_side_effect

        # 2. Act
        ltv = self.customer_service.get_customer_lifetime_value("C1")

        # 3. Assert
        self.assertEqual(ltv, 100.0) # Should just ignore order 99
        self.mock_data_store.orders.get.assert_has_calls([call(1), call(99)])

    def test_check_and_upgrade_membership_customer_not_found(self):
        """
        Tests the upgrade check when the customer ID is not found.
        (Covers line 124)
        """
        # 1. Arrange
        self.mock_data_store.get_customer.return_value = None
        
        # 2. Act
        result = self.customer_service.check_and_upgrade_membership("C_BAD")
        
        # 3. Assert
        self.assertFalse(result)

    def test_check_and_upgrade_membership_suspended(self):
        """
        Tests that a suspended customer cannot be upgraded.
        (Covers line 128)
        """
        # 1. Arrange
        mock_customer = MagicMock(customer_id="C_SUSPENDED")
        mock_customer.membership_tier = SuspendedMembership()
        
        self.mock_data_store.get_customer.return_value = mock_customer
        
        # 2. Act
        result = self.customer_service.check_and_upgrade_membership("C_SUSPENDED")
        
        # 3. Assert
        self.assertFalse(result)
        # We should not even bother calculating LTV
        self.assertEqual(mock_customer.membership_tier.get_name(), 'suspended')


    def test_check_and_upgrade_membership_to_silver(self):
        """
        Tests a customer upgrading from Bronze to Silver.
        """
        # 1. Arrange
        mock_customer = MagicMock(customer_id="C1")
        mock_customer.membership_tier = BronzeMembership()
        
        self.mock_data_store.get_customer.return_value = mock_customer
        
        with patch.object(self.customer_service, 'get_customer_lifetime_value', return_value=600.0) as mock_get_ltv:
            # 2. Act
            result = self.customer_service.check_and_upgrade_membership("C1")

        # 3. Assert
        self.assertTrue(result)
        mock_get_ltv.assert_called_once_with("C1")
        self.assertIsInstance(mock_customer.membership_tier, SilverMembership)

    def test_check_and_upgrade_membership_to_gold(self):
        """
        Tests a customer upgrading from Bronze directly to Gold.
        """
        # 1. Arrange
        mock_customer = MagicMock(customer_id="C2")
        mock_customer.membership_tier = BronzeMembership()
        
        self.mock_data_store.get_customer.return_value = mock_customer
        
        with patch.object(self.customer_service, 'get_customer_lifetime_value', return_value=1100.0) as mock_get_ltv:
            # 2. Act
            result = self.customer_service.check_and_upgrade_membership("C2")

        # 3. Assert
        self.assertTrue(result)
        mock_get_ltv.assert_called_once_with("C2")
        self.assertIsInstance(mock_customer.membership_tier, GoldMembership)

    def test_check_and_upgrade_membership_no_upgrade(self):
        """
        Tests that no upgrade occurs if LTV is too low.
        """
        # 1. Arrange
        mock_customer = MagicMock(customer_id="C3")
        mock_customer.membership_tier = BronzeMembership()
        
        self.mock_data_store.get_customer.return_value = mock_customer
        
        with patch.object(self.customer_service, 'get_customer_lifetime_value', return_value=450.0) as mock_get_ltv:
            # 2. Act
            result = self.customer_service.check_and_upgrade_membership("C3")

        # 3. Assert
        self.assertFalse(result)
        mock_get_ltv.assert_called_once_with("C3")
        self.assertIsInstance(mock_customer.membership_tier, BronzeMembership)

    # --- THE FIX IS HERE ---
    # 1. We patch the *module* 'datetime' as it's seen by the customer_service file.
    @patch('submission.services.customer_service.datetime')
    def test_get_customers_for_segment_inactive(self, mock_datetime_module):
        """
        Tests the 'inactive' segment, which requires date logic.
        (Covers lines 143-156)
        """
        # 1. Arrange
        
        # --- Set up a fixed "now" ---
        # Create a *real* datetime object
        real_now = datetime.datetime(2023, 10, 1) # Oct 1st, 2023
        
        # 2. Configure the mock module:
        # - Tell .datetime.now() to return our real 'now'
        mock_datetime_module.datetime.now.return_value = real_now
        # - Tell .timedelta() to use the *real* timedelta class
        mock_datetime_module.timedelta = datetime.timedelta
        
        # --- Create mock customers ---
        cust_active = MagicMock(order_history=[1])
        cust_inactive = MagicMock(order_history=[2])
        cust_no_orders = MagicMock(order_history=[])
        
        # --- Create mock orders with real dates ---
        order_recent = MagicMock(created_at = real_now - datetime.timedelta(days=30))
        order_old = MagicMock(created_at = real_now - datetime.timedelta(days=100))
        
        # --- Configure DataStore mocks ---
        self.mock_data_store.customers.values.return_value = [cust_active, cust_inactive, cust_no_orders]
        
        def get_order_side_effect(order_id):
            if order_id == 1: return order_recent
            if order_id == 2: return order_old
            return None
        self.mock_data_store.orders.get.side_effect = get_order_side_effect

        # 2. Act
        inactive_list = self.customer_service.get_customers_for_segment('inactive')
        
        # 3. Assert
        self.assertEqual(len(inactive_list), 2)
        self.assertIn(cust_inactive, inactive_list)
        self.assertIn(cust_no_orders, inactive_list)
        self.assertNotIn(cust_active, inactive_list)

    def test_get_customers_for_segment_gold(self):
        """
        Tests the 'gold' segment.
        (Covers line 140)
        """
        # 1. Arrange
        cust_gold = MagicMock()
        cust_gold.membership_tier.get_name.return_value = 'gold'
        
        cust_silver = MagicMock()
        cust_silver.membership_tier.get_name.return_value = 'silver'
        
        self.mock_data_store.customers.values.return_value = [cust_gold, cust_silver]
        
        # 2. Act
        gold_list = self.customer_service.get_customers_for_segment('gold')
        
        # 3. Assert
        self.assertEqual(gold_list, [cust_gold])

    def test_get_customers_for_segment_all(self):
        """
        Tests the 'all' segment.
        (Covers line 137)
        """
        # 1. Arrange
        cust1 = MagicMock()
        cust2 = MagicMock()
        all_custs = [cust1, cust2]
        
        self.mock_data_store.customers.values.return_value = all_custs
        
        # 2. Act
        all_list = self.customer_service.get_customers_for_segment('all')
        
        # 3. Assert
        self.assertEqual(all_list, all_custs)
