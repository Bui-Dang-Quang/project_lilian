import datetime
from typing import List, Optional

class OrderItem:
    def __init__(
        self, 
        product_id: str, 
        quantity: int, 
        unit_price: float
    ) -> None:
        self.product_id: str = product_id
        self.quantity: int = quantity
        self.unit_price: float = unit_price
        self.discount_applied: float = 0.0
