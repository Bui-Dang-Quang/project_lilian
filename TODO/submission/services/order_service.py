from abc import ABC, abstractmethod
import datetime
import random
from typing import List, Optional

# --- Import Dependencies ---
from submission.repositories.in_memory.DataStore import DataStore
from submission.domain.models.Order import Order
from submission.domain.models.OrderItem import OrderItem
from submission.domain.models.Customer import Customer
from submission.domain.enums.order_status import OrderStatus

# --- Import Service Interfaces ---
from submission.services.notification_service import NotificationInterface
from submission.services.shipping_service import ShippingServiceInterface
from submission.services.inventory_service import InventoryInterface
from submission.services.customer_service import CustomerInterface

# --- Interface ---
class OrderInterface(ABC):
    @abstractmethod
    def create_order(
        self, 
        customer_id: str, 
        order_items: List[OrderItem], 
        total_price: float, 
        shipping_cost: float, 
        payment_method: str
    ) -> Order:
        pass  # pragma: no cover
        
    @abstractmethod
    def get_order(self, order_id: int) -> Optional[Order]:
        pass  # pragma: no cover
        
    @abstractmethod
    def update_order_status(self, order_id: int, new_status: OrderStatus) -> Optional[Order]:
        pass  # pragma: no cover

    @abstractmethod
    def apply_additional_discount(
        self,  # <-- Added 'self'
        order_id: int, 
        discount_percent: float, 
        reason: str
    ) -> Optional[Order]:
        pass  # pragma: no cover

    @abstractmethod
    def cancel_order(self, order_id: int, reason: str) -> bool:
        pass  # pragma: no cover

    @abstractmethod
    def get_customer_orders(self, customer_id: str) -> List[Order]:
        pass  # pragma: no cover

# --- Concrete Class ---
class OrderService(OrderInterface):
    def __init__(
        self, 
        data_store: DataStore, 
        notification_service: NotificationInterface, 
        shipping_service: ShippingServiceInterface,  # <-- Use Interface
        inventory_service: InventoryInterface, 
        customer_service: CustomerInterface  # <-- Use Interface
    ) -> None:
        
        self.data_store: DataStore = data_store
        self.notification_service: NotificationInterface = notification_service
        self.shipping_service: ShippingServiceInterface = shipping_service
        self.inventory_service: InventoryInterface = inventory_service
        self.customer_service: CustomerInterface = customer_service

    def create_order(
        self, 
        customer_id: str, 
        order_items: List[OrderItem], 
        total_price: float, 
        shipping_cost: float, 
        payment_method: str
    ) -> Order:
        
        order_id: int = self.data_store.next_order_id
        self.data_store.next_order_id += 1

        order = Order(
            order_id=order_id,
            customer_id=customer_id,
            items=order_items,
            status=OrderStatus.PENDING,  # <-- Use Enum
            created_at=datetime.datetime.now(),
            total_price=total_price,
            shipping_cost=shipping_cost
        )
        order.payment_method = payment_method
        self.data_store.orders[order_id] = order

        return order

    def get_order(self, order_id: int) -> Optional[Order]:
        order: Optional[Order] = self.data_store.orders.get(order_id)
        if not order:
            return None
        return order
    
    def update_order_status(self, order_id: int, new_status: OrderStatus) -> Optional[Order]:
        order: Optional[Order] = self.get_order(order_id)
        if not order:
            return None
            
        order.status = new_status

        customer: Optional[Customer] = self.data_store.get_customer(order.customer_id)
        
        if customer:
            self.notification_service.send_status_update(customer, order)
        
        if new_status == OrderStatus.SHIPPED and not order.tracking_number: # <-- Use Enum
            try: 
                tracking_number: str = self.shipping_service.create_shipment_for_order(order)
                order.tracking_number = tracking_number
            except Exception as e:
                print(f"Warning: Failed to create shipment for order {order_id}: {e}")
                return None
        return order
    
    def apply_additional_discount(
        self, 
        order_id: int, 
        discount_percent: float, 
        reason: str
    ) -> Optional[Order]:
        
        order: Optional[Order] = self.get_order(order_id)
        if not order:
            return None

        if order.status != OrderStatus.PENDING: # <-- Use Enum
            print("Can only apply discount to pending orders")
            return None

        order.total_price = order.total_price * (1 - discount_percent / 100)
        print(f"Applied {discount_percent}% discount to order {order_id}. New total: ${order.total_price:.2f}. Reason: {reason}")
        return order
    
    def cancel_order(self, order_id: int, reason: str) -> bool:
        order: Optional[Order] = self.get_order(order_id)
        if not order:
            return False

        if order.status in [OrderStatus.SHIPPED, OrderStatus.DELIVERED]: # <-- Use Enum
            print(f"Cannot cancel order in {order.status} status")
            return False
        
        if order.status == OrderStatus.CANCELLED: # <-- Use Enum
            return True
        
        self.inventory_service.restore_stock(order)

        order.status = OrderStatus.CANCELLED # <-- Use Enum

        customer: Optional[Customer] = self.data_store.get_customer(order.customer_id)
        if customer:
            self.notification_service.send_cancellation_notice(customer, order, reason)
            self.customer_service.refund_loyalty_points_for_order(customer, order)

        return True
    
    def get_customer_orders(self, customer_id: str) -> List[Order]:
        customer_orders: List[Order] = [] # <-- Fixed typo

        for order in self.data_store.orders.values():
            if order.customer_id == customer_id:
                customer_orders.append(order)

        return customer_orders
