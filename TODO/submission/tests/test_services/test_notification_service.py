import unittest
from unittest.mock import MagicMock, patch
import io # Used to capture stdout

# Import the class we are testing
from submission.services.notification_service import NotificationService

# We will use MagicMock to create stand-ins for
# the domain models (Customer, Order).

class TestNotificationService(unittest.TestCase):

    def setUp(self):
        """
        Set up a fresh service for each test.
        """
        self.notification_service = NotificationService()

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_send_order_confirmation_with_phone(self, mock_stdout):
        """
        Tests that both email and SMS are sent if a phone number exists.
        """
        # 1. Arrange
        mock_customer = MagicMock()
        mock_customer.email = "test@example.com"
        mock_customer.phone = "123456789"
        
        mock_order = MagicMock()
        mock_order.order_id = 101
        mock_order.total_price = 75.50
        
        # 2. Act
        self.notification_service.send_order_confirmation(mock_customer, mock_order)
        
        # 3. Assert
        output = mock_stdout.getvalue()
        # Check that the email message is present
        self.assertIn("Email to test@example.com: Order 101 confirmed! Total: $75.50", output)
        # Check that the SMS message is present
        self.assertIn("SMS to 123456789: Order 101 confirmed", output)

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_send_order_confirmation_no_phone(self, mock_stdout):
        """
        Tests that only email is sent if no phone number exists.
        """
        # 1. Arrange
        mock_customer = MagicMock()
        mock_customer.email = "no-phone@example.com"
        mock_customer.phone = None # Explicitly set to None
        
        mock_order = MagicMock()
        mock_order.order_id = 102
        mock_order.total_price = 25.00
        
        # 2. Act
        self.notification_service.send_order_confirmation(mock_customer, mock_order)
        
        # 3. Assert
        output = mock_stdout.getvalue()
        # Check that the email message is present
        self.assertIn("Email to no-phone@example.com: Order 102 confirmed! Total: $25.00", output)
        # Check that the SMS message is *not* present
        self.assertNotIn("SMS to", output)

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_send_status_update(self, mock_stdout):
        """
        Tests the order status update notification.
        """
        # 1. Arrange
        mock_customer = MagicMock()
        mock_customer.email = "status@example.com"
        
        mock_order = MagicMock()
        mock_order.order_id = 200
        mock_order.status = "shipped"
        
        # 2. Act
        self.notification_service.send_status_update(mock_customer, mock_order)
        
        # 3. Assert
        expected_output = "Email to status@example.com: Order 200 status changed to shipped\n"
        self.assertEqual(mock_stdout.getvalue(), expected_output)

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_send_cancellation_notice(self, mock_stdout):
        """
        Tests the order cancellation notification.
        """
        # 1. Arrange
        mock_customer = MagicMock()
        mock_customer.email = "cancel@example.com"
        
        mock_order = MagicMock()
        mock_order.order_id = 300
        
        reason = "Out of stock"
        
        # 2. Act
        self.notification_service.send_cancellation_notice(mock_customer, mock_order, reason)
        
        # 3. Assert
        expected_output = "To: cancel@example.com: Order 300 has been cancelled. Reason: Out of stock\n"
        self.assertEqual(mock_stdout.getvalue(), expected_output)

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_send_marketing_email(self, mock_stdout):
        """
        Tests sending marketing emails to a list of customers and returns the count.
        """
        # 1. Arrange
        cust1 = MagicMock(email="cust1@dev.com")
        cust2 = MagicMock(email="cust2@dev.com")
        customers_list = [cust1, cust2]
        message = "Big sale!"
        
        # 2. Act
        count = self.notification_service.send_marketing_email(customers_list, message)
        
        # 3. Assert
        # Check the returned count
        self.assertEqual(count, 2)
        
        # Check the printed output
        output = mock_stdout.getvalue()
        self.assertIn("Email to cust1@dev.com: Big sale!", output)
        self.assertIn("Email to cust2@dev.com: Big sale!", output)

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_send_marketing_email_empty_list(self, mock_stdout):
        """
        Tests that no emails are sent and count is 0 for an empty list.
        """
        # 1. Arrange
        customers_list = []
        message = "Big sale!"
        
        # 2. Act
        count = self.notification_service.send_marketing_email(customers_list, message)
        
        # 3. Assert
        # Check the returned count
        self.assertEqual(count, 0)
        
        # Check that nothing was printed
        output = mock_stdout.getvalue()
        self.assertEqual(output, "")

