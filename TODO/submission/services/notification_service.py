from __future__ import annotations  # Enables modern type hinting
from abc import ABC, abstractmethod
from typing import List

# Import the domain models for type hinting
from submission.domain.models.Customer import Customer
from submission.domain.models.Order import Order

class NotificationInterface(ABC):

    @abstractmethod
    def send_order_confirmation(self, customer: Customer, order: Order) -> None:
        """Sends an order confirmation email and SMS."""
        pass  # pragma: no cover

    @abstractmethod
    def send_status_update(self, customer: Customer, order: Order) -> None:
        """Sends an order status update email."""
        pass  # pragma: no cover

    @abstractmethod
    def send_cancellation_notice(self, customer: Customer, order: Order, reason: str) -> None:
        """Sends an order cancellation email."""
        pass  # pragma: no cover

    @abstractmethod
    def send_marketing_email(self, customers: List[Customer], message: str) -> int:
        """Sends a marketing email to a list of customers and returns the count."""
        pass  # pragma: no cover

class NotificationService(NotificationInterface):

    def send_order_confirmation(self, customer: Customer, order: Order) -> None:
        """
        Sends notification (stubbed as print) for a new order.
        """
        print(f"Email to {customer.email}: Order {order.order_id} confirmed! Total: ${order.total_price:.2f}")
        
        if customer.phone:
            print(f"SMS to {customer.phone}: Order {order.order_id} confirmed")

    def send_status_update(self, customer: Customer, order: Order) -> None:
        """
        Sends notification (stubbed as print) for a status change.
        """
        print(f"Email to {customer.email}: Order {order.order_id} status changed to {order.status}")

    def send_cancellation_notice(self, customer: Customer, order: Order, reason: str) -> None:
        """
        Sends notification (stubbed as print) for a cancelled order.
        """
        print(f"To: {customer.email}: Order {order.order_id} has been cancelled. Reason: {reason}")
    
    def send_marketing_email(self, customers: List[Customer], message: str) -> int:
        """
        Sends marketing emails (stubbed as print) to a list of customers.
        """
        count: int = 0
        for customer in customers:
            print(f"Email to {customer.email}: {message}")
            count += 1
        
        return count
