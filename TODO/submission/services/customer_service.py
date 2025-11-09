from abc import ABC, abstractmethod
from typing import List, Optional, Iterable
import datetime

# --- Import Dependencies ---
from submission.repositories.in_memory.DataStore import DataStore
from submission.domain.models.Customer import Customer
from submission.domain.models.Order import Order
from submission.services.pricing.strategies.membership_discount import (
    MembershipTier,
    BronzeMembership,
    SilverMembership,
    GoldMembership
)

# --- Interface ---
class CustomerInterface(ABC):
    
    @abstractmethod
    def finalize_customer_order_updates(self, customer: Customer, order_id: int, subtotal: float) -> None:
        """
        Handles post-order updates to the customer's profile,
        like updating history and awarding loyalty points.
        """
        pass  # pragma: no cover

    @abstractmethod
    def refund_loyalty_points_for_order(self, customer: Customer, order: Order) -> None:
        """
        Refunds loyalty points that were spent on a cancelled order.
        """
        pass  # pragma: no cover

    @abstractmethod
    def get_customer_lifetime_value(self, customer_id: str) -> float:
        """
        Calculates the total value of a customer's non-cancelled orders.
        """
        pass  # pragma: no cover

    @abstractmethod
    def check_and_upgrade_membership(self, customer_id: str) -> bool:
        """
        Checks a customer's LTV and upgrades their membership
        tier if they qualify.
        """
        pass  # pragma: no cover

    @abstractmethod
    def get_customers_for_segment(self, segment: str) -> List[Customer]:
        """
        Gets a list of customers based on a marketing segment.
        """
        pass  # pragma: no cover

# --- Concrete Class ---
class CustomerService(CustomerInterface):
    def __init__(self, data_store: DataStore) -> None:
        self.data_store: DataStore = data_store

    def finalize_customer_order_updates(self, customer: Customer, order_id: int, subtotal: float) -> None:
        """
        Updates customer history and awards loyalty points.
        Note: This method name was updated from 'customer_order_updates' to match.
        """
        customer.order_history.append(order_id)
        customer.loyalty_points += int(subtotal)

    def refund_loyalty_points_for_order(self, customer: Customer, order: Order) -> None:
        """
        Logs that a loyalty point refund is being processed.
        (Logic is a placeholder as per original code).
        """
        print(f"Processing loyalty point refund for {customer.name} for order {order.order_id}.")

    def get_customer_lifetime_value(self, customer_id: str) -> float:
        """
        Calculates the total value of a customer's non-cancelled orders.
        """
        customer: Optional[Customer] = self.data_store.get_customer(customer_id)
        if not customer:
            return 0.0

        total_value: float = 0.0
        for order_id in customer.order_history:
            order: Optional[Order] = self.data_store.orders.get(order_id)
            
            if order and order.status != 'cancelled':
                total_value += order.total_price

        return total_value
    
    def check_and_upgrade_membership(self, customer_id: str) -> bool:
        """
        Checks a customer's LTV and upgrades their membership
        tier if they qualify.
        """
        customer: Optional[Customer] = self.data_store.get_customer(customer_id)
        if not customer:
            return False

        current_tier_name: str = customer.membership_tier.get_name()

        # Your logic: If suspended, do nothing.
        if current_tier_name == 'suspended':
            return False

        lifetime_value: float = self.get_customer_lifetime_value(customer_id)
        new_tier_object: Optional[MembershipTier] = None

        # Logic fixed: Check from highest to lowest
        # and only upgrade from a lower tier.
        if lifetime_value >= 1000 and current_tier_name != 'gold':
            new_tier_object = GoldMembership()
            print(f"Customer {customer.name} upgraded to Gold!")
        elif lifetime_value >= 500 and current_tier_name == 'bronze':
            new_tier_object = SilverMembership()
            print(f"Customer {customer.name} upgraded to Silver!")
        
        # (The 'standard' to 'bronze' rule is removed as 
        # 'bronze' is the new base tier)

        if new_tier_object:
            customer.membership_tier = new_tier_object
            return True

        return False
    
    def get_customers_for_segment(self, segment: str) -> List[Customer]:
        """
        Gets a list of customers based on a marketing segment.
        """
        targeted_customers: List[Customer] = []
        all_customers: Iterable[Customer] = self.data_store.customers.values()

        if segment == 'all':
            return list(all_customers)

        for customer in all_customers:
            if segment == 'gold' and customer.membership_tier.get_name() == 'gold':
                targeted_customers.append(customer)
            
            elif segment == 'inactive':
                has_recent_order: bool = False
                cutoff: datetime.datetime = datetime.datetime.now() - datetime.timedelta(days=90)
                
                for order_id in customer.order_history:
                    order: Optional[Order] = self.data_store.orders.get(order_id)
                    if order and order.created_at > cutoff:
                        has_recent_order = True
                        break
                
                if not has_recent_order:
                    targeted_customers.append(customer)
        
        return targeted_customers
