from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple, Optional

# Import the strategies
from .pricing.strategies.payment_strategy import (
    PaymentStrategy, 
    CreditCardStrategy, 
    PayPalStrategy, 
    UnknownPaymentStrategy
)

class PaymentServiceInterface(ABC):
    """
    Interface for the PaymentService.
    """
    @abstractmethod
    def validate_payment(
        self, 
        payment_info: Dict[str, Any], 
        total_amount: float
    ) -> Tuple[bool, str]:
        """
        Validates a payment using both shared and specific logic.
        """
        pass  # pragma: no cover  <--- FIX

class PaymentService(PaymentServiceInterface):
    """
    Validates and processes a payment by selecting the correct
    payment strategy.
    """
    def __init__(self) -> None:
        self.strategies: Dict[str, PaymentStrategy] = {
            "credit_card": CreditCardStrategy(),
            "paypal": PayPalStrategy()
        }
        self._default_strategy: PaymentStrategy = UnknownPaymentStrategy()

    def validate_payment(
        self, 
        payment_info: Dict[str, Any], 
        total_amount: float
    ) -> Tuple[bool, str]:
        
        if not payment_info.get("valid"):
            return False, "Payment failed - invalid payment info"

        payment_amount: float = payment_info.get("amount", 0.0)
        rounded_total: float = round(total_amount, 2)

        if payment_amount < rounded_total:
            return False, "Insufficient payment amount"

        payment_type: Optional[str] = payment_info.get("type")
        
        strategy: PaymentStrategy
        if payment_type is None:
            strategy = self._default_strategy
        else:
            strategy = self.strategies.get(payment_type, self._default_strategy)
        
        is_valid: bool
        error_message: str
        is_valid, error_message = strategy.validate(payment_info)
        
        if not is_valid:
            return False, error_message

        return True, "Payment successful"
