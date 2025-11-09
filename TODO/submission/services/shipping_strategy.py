from abc import ABC, abstractmethod
from submission.domain.models.Customer import Customer

# --- Strategy Interface ---
class ShippingStrategy(ABC):
    @abstractmethod
    def cal_shipping_cost(
        self, 
        total_weight: float, 
        customer: Customer, 
        subtotal: float
    ) -> float:
        pass # pragma: no cover

# --- Concrete Strategies ---
class ExpressShipping(ShippingStrategy):
    def cal_shipping_cost(
        self, 
        total_weight: float, 
        customer: Customer, 
        subtotal: float
    ) -> float:
        shipping_cost: float = 25.0 + (total_weight * 0.5)
        if customer.membership_tier.get_name() == "gold":
            shipping_cost *= 0.5
        return shipping_cost

class StandardShipping(ShippingStrategy):
    def cal_shipping_cost(
        self, 
        total_weight: float, 
        customer: Customer,
        subtotal: float
    ) -> float:
        if subtotal < 50:
            shipping_cost: float = 5.0 + (total_weight * 0.2)
        else: 
            shipping_cost = 0.0 # Free shipping
        return shipping_cost

class OvernightShipping(ShippingStrategy):
    def cal_shipping_cost(
        self, 
        total_weight: float, 
        customer: Customer,
        subtotal: float
    ) -> float:
        shipping_cost: float = 50.0 + (total_weight * 1.0)
        return shipping_cost
