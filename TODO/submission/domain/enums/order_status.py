from enum import Enum

class OrderStatus(Enum):
    """
    Represents the valid statuses for an Order.
    """
    PENDING = "pending"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"