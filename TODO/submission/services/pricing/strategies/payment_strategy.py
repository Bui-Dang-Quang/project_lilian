from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple

class PaymentStrategy(ABC):
    """
    The 'Strategy' interface for all payment processing methods.
    """
    @abstractmethod
    def validate(self, payment_info: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validates the payment-specific details (e.g., card number, email).
        Returns a (bool, str) tuple: (is_valid, error_message).
        """
        pass  # pragma: no cover

class CreditCardStrategy(PaymentStrategy):
    """Handles credit card validation logic."""
    def validate(self, payment_info: Dict[str, Any]) -> Tuple[bool, str]:
        card_number: str = payment_info.get("card_number", "")
        if len(card_number) < 16:
            return False, "Invalid card number"
        return True, ""

class PayPalStrategy(PaymentStrategy):
    """Handles PayPal validation logic."""
    def validate(self, payment_info: Dict[str, Any]) -> Tuple[bool, str]:
        email: str = payment_info.get("email", "")
        if not email:
            return False, "PayPal email required"
        # In a real app, you would also validate the email format here
        return True, ""

class UnknownPaymentStrategy(PaymentStrategy):
    """A 'null' strategy for unhandled payment types."""
    def validate(self, payment_info: Dict[str, Any]) -> Tuple[bool, str]:
        return False, "Unknown payment type"
