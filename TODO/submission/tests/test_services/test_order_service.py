import unittest
from unittest.mock import MagicMock, patch, call
import io
import datetime

# Import the class we are testing
from submission.services.order_service import OrderService

# Import the Enum for status checks
from submission.domain.enums.order_status import OrderStatus

# We will use MagicMock for all dependencies and models
# (DataStore, Services, Customer, Order)

class TestOrderService(unittest.TestCase):

    def setUp(self):
        """
        Set up a fresh service and mocks for all five dependencies.
        """
        self.mock_data_store = MagicMock()
        self.mock_notification_service = MagicMock()
        self.mock_shipping_service = MagicMock()
        self.mock_inventory_service = MagicMock()
        self.mock_customer_service = MagicMock()
        
        # Instantiate the service with all mocks
        self.order_service = OrderService(
            data_store=self.mock_data_store,
            notification_service=self.mock_notification_service,
            shipping_service=self.mock_shipping_service,
            inventory_service=self.mock_inventory_service,
            customer_service=self.mock_customer_service
        )
        
        # Mock a customer and order for convenience
        self.mock_order = MagicMock(
            order_id=1, 
            customer_id="C1",
            status=OrderStatus.PENDING,
            tracking_number=None,
            total_price=100.0
        )
        self.mock_customer = MagicMock(customer_id="C1")

    @patch('submission.services.order_service.datetime')
    def test_create_order(self, mock_datetime):
        """
        Tests that an order is created, saved, and returned correctly.
        """
        # 1. Arrange
        mock_now = datetime.datetime(2023, 1, 1, 12, 0, 0)
        mock_datetime.datetime.now.return_value = mock_now
        
        self.mock_data_store.next_order_id = 101
        self.mock_data_store.orders = {}
        
        mock_items = [MagicMock()]
        
        # 2. Act
        new_order = self.order_service.create_order(
            customer_id="C1",
            order_items=mock_items,
            total_price=150.0,
            shipping_cost=10.0,
            payment_method="credit_card"
        )
        
        # 3. Assert
        self.assertEqual(self.mock_data_store.next_order_id, 102)
        self.assertEqual(new_order.order_id, 101)
        self.assertEqual(new_order.customer_id, "C1")
        self.assertEqual(new_order.items, mock_items)
        self.assertEqual(new_order.status, OrderStatus.PENDING)
        self.assertEqual(new_order.created_at, mock_now)
        self.assertEqual(new_order.total_price, 150.0)
        self.assertEqual(new_order.shipping_cost, 10.0)
        self.assertEqual(new_order.payment_method, "credit_card")
        self.assertEqual(self.mock_data_store.orders[101], new_order)

    def test_get_order_found(self):
        """
        Tests retrieving an existing order.
        """
        # 1. Arrange
        self.mock_data_store.orders.get.return_value = self.mock_order
        
        # 2. Act
        order = self.order_service.get_order(1)
        
        # 3. Assert
        self.assertEqual(order, self.mock_order)
        self.mock_data_store.orders.get.assert_called_once_with(1)

    def test_get_order_not_found(self):
        """
        Tests retrieving a non-existent order.
        (Covers line 109)
        """
        # 1. Arrange
        self.mock_data_store.orders.get.return_value = None
        
        # 2. Act
        order = self.order_service.get_order(99)
        
        # 3. Assert
        self.assertIsNone(order)
        self.mock_data_store.orders.get.assert_called_once_with(99)

    def test_update_order_status_to_shipped_and_create_shipment(self):
        """
        Tests that updating status to SHIPPED also creates a shipment.
        """
        # 1. Arrange
        with patch.object(self.order_service, 'get_order', return_value=self.mock_order):
            self.mock_data_store.get_customer.return_value = self.mock_customer
            self.mock_shipping_service.create_shipment_for_order.return_value = "123XYZ"
            
            # 2. Act
            updated_order = self.order_service.update_order_status(1, OrderStatus.SHIPPED)
        
        # 3. Assert
        self.assertEqual(updated_order, self.mock_order)
        self.assertEqual(self.mock_order.status, OrderStatus.SHIPPED)
        self.mock_notification_service.send_status_update.assert_called_once_with(
            self.mock_customer, self.mock_order
        )
        self.mock_shipping_service.create_shipment_for_order.assert_called_once_with(self.mock_order)
        self.assertEqual(self.mock_order.tracking_number, "123XYZ")

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_update_order_status_shipping_failure(self, mock_stdout):
        """
        Tests that an exception during shipment creation is caught and returns None.
        """
        # 1. Arrange
        with patch.object(self.order_service, 'get_order', return_value=self.mock_order):
            self.mock_data_store.get_customer.return_value = self.mock_customer
            self.mock_shipping_service.create_shipment_for_order.side_effect = Exception("API down")
            
            # 2. Act
            updated_order = self.order_service.update_order_status(1, OrderStatus.SHIPPED)
        
        # 3. Assert
        self.assertIsNone(updated_order)
        self.mock_notification_service.send_status_update.assert_called_once()
        self.assertIn("Warning: Failed to create shipment", mock_stdout.getvalue())

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_apply_discount_success(self, mock_stdout):
        """
        Tests applying a discount to a PENDING order.
        """
        # 1. Arrange
        with patch.object(self.order_service, 'get_order', return_value=self.mock_order):
            # 2. Act
            updated_order = self.order_service.apply_additional_discount(1, 10, "Courtesy")
        
        # 3. Assert
        self.assertEqual(updated_order, self.mock_order)
        self.assertEqual(self.mock_order.total_price, 90.0) # 100 * (1 - 0.10)
        self.assertIn("Applied 10% discount", mock_stdout.getvalue())
        
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_apply_discount_fail_not_pending(self, mock_stdout):
        """
        Tests that a discount cannot be applied to a non-PENDING order.
        """
        # 1. Arrange
        self.mock_order.status = OrderStatus.SHIPPED
        with patch.object(self.order_service, 'get_order', return_value=self.mock_order):
            # 2. Act
            updated_order = self.order_service.apply_additional_discount(1, 10, "Too late")
        
        # 3. Assert
        self.assertIsNone(updated_order)
        self.assertEqual(self.mock_order.total_price, 100.0)
        self.assertIn("Can only apply discount to pending orders", mock_stdout.getvalue())

    def test_cancel_order_success(self):
        """
        Tests a successful order cancellation (restores stock, notifies).
        """
        # 1. Arrange
        with patch.object(self.order_service, 'get_order', return_value=self.mock_order):
            self.mock_data_store.get_customer.return_value = self.mock_customer
            
            # 2. Act
            result = self.order_service.cancel_order(1, "Changed mind")
        
        # 3. Assert
        self.assertTrue(result)
        self.mock_inventory_service.restore_stock.assert_called_once_with(self.mock_order)
        self.assertEqual(self.mock_order.status, OrderStatus.CANCELLED)
        self.mock_notification_service.send_cancellation_notice.assert_called_once_with(
            self.mock_customer, self.mock_order, "Changed mind"
        )
        self.mock_customer_service.refund_loyalty_points_for_order.assert_called_once_with(
            self.mock_customer, self.mock_order
        )

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_cancel_order_fail_shipped(self, mock_stdout):
        """
        Tests that a SHIPPED order cannot be cancelled.
        """
        # 1. Arrange
        self.mock_order.status = OrderStatus.SHIPPED
        with patch.object(self.order_service, 'get_order', return_value=self.mock_order):
            # 2. Act
            result = self.order_service.cancel_order(1, "Too late")
            
        # 3. Assert
        self.assertFalse(result)
        self.mock_inventory_service.restore_stock.assert_not_called()
        self.mock_notification_service.send_cancellation_notice.assert_not_called()
        self.assertIn("Cannot cancel order", mock_stdout.getvalue())

    def test_cancel_order_customer_not_found(self):
        """
        Tests cancellation still works (restores stock) even if customer is not found.
        """
        # 1. Arrange
        with patch.object(self.order_service, 'get_order', return_value=self.mock_order):
            self.mock_data_store.get_customer.return_value = None
            
            # 2. Act
            result = self.order_service.cancel_order(1, "Changed mind")
        
        # 3. Assert
        self.assertTrue(result)
        self.mock_inventory_service.restore_stock.assert_called_once_with(self.mock_order)
        self.assertEqual(self.mock_order.status, OrderStatus.CANCELLED)
        self.mock_notification_service.send_cancellation_notice.assert_not_called()
        self.mock_customer_service.refund_loyalty_points_for_order.assert_not_called()

    def test_get_customer_orders(self):
        """
        Tests retrieving all orders for a specific customer.
        """
        # 1. Arrange
        order1 = MagicMock(customer_id="C1")
        order2 = MagicMock(customer_id="C2")
        order3 = MagicMock(customer_id="C1")
        
        all_orders = [order1, order2, order3]
        self.mock_data_store.orders.values.return_value = all_orders
        
        # 2. Act
        customer_orders = self.order_service.get_customer_orders("C1")
        
        # 3. Assert
        self.assertEqual(len(customer_orders), 2)
        self.assertIn(order1, customer_orders)
        self.assertIn(order3, customer_orders)
        self.assertNotIn(order2, customer_orders)

    def test_get_customer_orders_no_orders(self):
        """
        Tests retrieving orders for a customer who has none.
        """
        # 1. Arrange
        order1 = MagicMock(customer_id="C1")
        order2 = MagicMock(customer_id="C2")
        
        all_orders = [order1, order2]
        self.mock_data_store.orders.values.return_value = all_orders
        
        # 2. Act
        customer_orders = self.order_service.get_customer_orders("C3") # No orders for C3
        
        # 3. Assert
        self.assertEqual(len(customer_orders), 0)

    # --- NEW TESTS TO FIX COVERAGE ---

    def test_update_order_status_order_not_found(self):
        """
        Tests that update_order_status returns None if the order is not found.
        (Covers line 136)
        """
        # 1. Arrange
        # We do *not* patch get_order. Instead, we mock the datastore.
        self.mock_data_store.orders.get.return_value = None
        
        # 2. Act
        result = self.order_service.update_order_status(99, OrderStatus.SHIPPED)
        
        # 3. Assert
        self.assertIsNone(result)
        # Ensure no other services were called
        self.mock_notification_service.send_status_update.assert_not_called()
        self.mock_shipping_service.create_shipment_for_order.assert_not_called()

    def test_apply_discount_order_not_found(self):
        """
        Tests that apply_additional_discount returns None if the order is not found.
        (Covers line 149)
        """
        # 1. Arrange
        self.mock_data_store.orders.get.return_value = None
        
        # 2. Act
        result = self.order_service.apply_additional_discount(99, 10, "Test")
        
        # 3. Assert
        self.assertIsNone(result)

    def test_cancel_order_order_not_found(self):
        """
        Tests that cancel_order returns False if the order is not found.
        (Covers line 156)
        """
        # 1. Arrange
        self.mock_data_store.orders.get.return_value = None
        
        # 2. Act
        result = self.order_service.cancel_order(99, "Test")
        
        # 3. Assert
        self.assertFalse(result)
        # Ensure no services were called
        self.mock_inventory_service.restore_stock.assert_not_called()
        self.mock_notification_service.send_cancellation_notice.assert_not_called()

    def test_cancel_order_already_cancelled(self):
        """
        Tests that cancelling an already-cancelled order just returns True.
        (Covers the 'if order.status == OrderStatus.CANCELLED' branch)
        """
        # 1. Arrange
        self.mock_order.status = OrderStatus.CANCELLED
        with patch.object(self.order_service, 'get_order', return_value=self.mock_order):
            # 2. Act
            result = self.order_service.cancel_order(1, "Test")
        
        # 3. Assert
        self.assertTrue(result)
        # Ensure no services were called
        self.mock_inventory_service.restore_stock.assert_not_called()
        self.mock_notification_service.send_cancellation_notice.assert_not_called()
