from abc import ABC, abstractmethod
import datetime
import random
from typing import Dict

# --- Import domain models ---
from submission.domain.models.Order import Order
from submission.domain.models.Customer import Customer
from submission.repositories.in_memory.DataStore import DataStore

# --- Import the strategies from their new file ---
from submission.services.shipping_strategy import (
    ShippingStrategy,
    StandardShipping,
    ExpressShipping,
    OvernightShipping
)

# --- Service Interface ---
class ShippingServiceInterface(ABC):
    @abstractmethod
    def shipping_cost(
        self, 
        shipping_method: str, 
        total_weight: float, 
        customer: Customer, 
        discounted_subtotal: float
    ) -> float:
        pass # pragma: no cover

    @abstractmethod
    def create_shipment_for_order(self, order: Order) -> str:
        pass # pragma: no cover

# --- Concrete Service ---
class ShippingService(ShippingServiceInterface):
    
    def __init__(self, data_store: DataStore):
        self.data_store = data_store
        # The strategies are now imported
        self.strategies: Dict[str, ShippingStrategy] = {
            'standard': StandardShipping(),
            'express': ExpressShipping(),
            'overnight': OvernightShipping()
        }
    
    def shipping_cost(
        self, 
        shipping_method: str, 
        total_weight: float, 
        customer: Customer, 
        discounted_subtotal: float
    ) -> float:
        
        shipping_strategy = self.strategies.get(shipping_method)
        if not shipping_strategy:
            raise ValueError(f"Invalid shipping method: {shipping_method}")
        return shipping_strategy.cal_shipping_cost(
            total_weight, customer, discounted_subtotal
        )
    
    def create_shipment_for_order(self, order: Order) -> str:
        tracking_number = f"TRACK{order.order_id}{random.randint(1000, 9999)}"
        
        shipment_id = self.data_store.next_shipment_id
        self.data_store.next_shipment_id += 1
        
        shipment_data = {
            'shipment_id': shipment_id,
            'order_id': order.order_id,
            'tracking_number': tracking_number,
            'created_at': datetime.datetime.now(),
            'status': 'in_transit'
        }
        
        self.data_store.shipments[shipment_id] = shipment_data
        
        return tracking_number
