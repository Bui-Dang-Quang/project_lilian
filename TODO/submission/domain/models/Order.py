import datetime
from typing import List, Optional
from submission.domain.enums.order_status import OrderStatus
from submission.domain.models.OrderItem import OrderItem

class Order:
    def __init__(
        self, 
        order_id: int, 
        customer_id: str, 
        items: List[OrderItem], 
        status: OrderStatus,
        created_at: datetime.datetime, 
        total_price: float, 
        shipping_cost: float
    ) -> None:
        self.order_id: int = order_id
        self.customer_id: str = customer_id
        self.items: List[OrderItem] = items
        self.status: OrderStatus = status
        self.created_at: datetime.datetime = created_at
        self.total_price: float = total_price
        self.shipping_cost: float = shipping_cost
        
        # These are None by default, so they are Optional
        self.tracking_number: Optional[str] = None
        self.payment_method: Optional[str] = None
