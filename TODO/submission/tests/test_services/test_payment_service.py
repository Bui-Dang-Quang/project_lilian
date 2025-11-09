import unittest
from typing import Dict, Any

# --- Import classes to be tested ---
from submission.services.pricing.strategies.payment_strategy import (
    CreditCardStrategy,
    PayPalStrategy,
    UnknownPaymentStrategy
)
from submission.services.payment_service import PaymentService

# --- Test the simple strategies ---
class TestPaymentStrategies(unittest.TestCase):

    def test_credit_card_strategy(self):
        strategy = CreditCardStrategy()
        
        # Test success
        valid_info = {"card_number": "1234567890123456"}
        is_valid, msg = strategy.validate(valid_info)
        self.assertTrue(is_valid)
        self.assertEqual(msg, "")
        
        # Test failure (too short)
        invalid_info = {"card_number": "12345"}
        is_valid, msg = strategy.validate(invalid_info)
        self.assertFalse(is_valid)
        self.assertEqual(msg, "Invalid card number")

    def test_paypal_strategy(self):
        strategy = PayPalStrategy()
        
        # Test success
        valid_info = {"email": "test@example.com"}
        is_valid, msg = strategy.validate(valid_info)
        self.assertTrue(is_valid)
        self.assertEqual(msg, "")
        
        # Test failure (no email)
        invalid_info = {"email": ""}
        is_valid, msg = strategy.validate(invalid_info)
        self.assertFalse(is_valid)
        self.assertEqual(msg, "PayPal email required")

    def test_unknown_strategy(self):
        strategy = UnknownPaymentStrategy()
        is_valid, msg = strategy.validate({}) # Input doesn't matter
        self.assertFalse(is_valid)
        self.assertEqual(msg, "Unknown payment type")

# --- Test the main service logic ---
class TestPaymentService(unittest.TestCase):

    def setUp(self):
        """Set up the service and a base payment info dict."""
        self.payment_service = PaymentService()
        self.total_amount = 100.0
        
        self.base_payment_info: Dict[str, Any] = {
            "valid": True,
            "type": "credit_card",
            "card_number": "1234567890123456",
            "amount": 100.0
        }

    def test_validate_payment_successful(self):
        """Test a fully successful payment."""
        is_valid, msg = self.payment_service.validate_payment(
            self.base_payment_info, self.total_amount
        )
        self.assertTrue(is_valid)
        self.assertEqual(msg, "Payment successful")

    def test_validate_fail_info_not_valid(self):
        """Test failure if the 'valid' flag is False."""
        self.base_payment_info["valid"] = False
        is_valid, msg = self.payment_service.validate_payment(
            self.base_payment_info, self.total_amount
        )
        self.assertFalse(is_valid)
        self.assertEqual(msg, "Payment failed - invalid payment info")

    def test_validate_fail_insufficient_amount(self):
        """Test failure if the payment amount is less than the total."""
        self.base_payment_info["amount"] = 99.99
        is_valid, msg = self.payment_service.validate_payment(
            self.base_payment_info, self.total_amount
        )
        self.assertFalse(is_valid)
        self.assertEqual(msg, "Insufficient payment amount")

    def test_validate_fail_delegates_to_credit_card(self):
        """Test failure is correctly delegated to the CreditCardStrategy."""
        self.base_payment_info["card_number"] = "123" # Too short
        is_valid, msg = self.payment_service.validate_payment(
            self.base_payment_info, self.total_amount
        )
        self.assertFalse(is_valid)
        self.assertEqual(msg, "Invalid card number")

    def test_validate_fail_delegates_to_paypal(self):
        """Test failure is correctly delegated to the PayPalStrategy."""
        self_paypal_info = {
            "valid": True, "type": "paypal",
            "email": "", "amount": 100.0 # Missing email
        }
        is_valid, msg = self.payment_service.validate_payment(
            self_paypal_info, self.total_amount
        )
        self.assertFalse(is_valid)
        self.assertEqual(msg, "PayPal email required")

    def test_validate_fail_delegates_to_unknown(self):
        """Test failure for an unknown payment type."""
        self.base_payment_info["type"] = "crypto" # Not in the strategies dict
        is_valid, msg = self.payment_service.validate_payment(
            self.base_payment_info, self.total_amount
        )
        self.assertFalse(is_valid)
        self.assertEqual(msg, "Unknown payment type")

    def test_validate_handles_rounding(self):
        """Test that validation correctly rounds the total."""
        tricky_total = 100.001
        self.base_payment_info["amount"] = 100.00
        
        # 100.00 is NOT less than 100.00 (after rounding total)
        is_valid, msg = self.payment_service.validate_payment(
            self.base_payment_info, tricky_total
        )
        self.assertTrue(is_valid) # Should pass

        # Now test failure
        self.base_payment_info["amount"] = 99.99
        is_valid, msg = self.payment_service.validate_payment(
            self.base_payment_info, tricky_total
        )
        self.assertFalse(is_valid)
        self.assertEqual(msg, "Insufficient payment amount")
