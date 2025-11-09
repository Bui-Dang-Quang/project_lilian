import datetime
from typing import Dict, List, Any, Optional

from submission.domain.models.Customer import Customer
from submission.domain.models.Order import Order
from submission.domain.models.OrderItem import OrderItem
from submission.domain.models.Supplier import Supplier
from submission.domain.models.Promotion import Promotion
from submission.domain.models.Product import Product
class DataStore:
    def __init__(self) -> None:
        self.products: Dict[str, Product] = {}
        self.customers: Dict[str, Customer] = {}
        self.orders: Dict[int, Order] = {}
        self.suppliers: Dict[str, Supplier] = {}
        self.promotions: Dict[str, Promotion] = {}
        self.shipments: Dict[int, Dict[str, Any]] = {}
        self.inventory_logs: List[Dict[str, Any]] = []

        # Incrementing IDs and shipment IDs
        self.next_order_id: int = 1
        self.next_shipment_id: int = 1
    
    def log_inventory_change(
        self, 
        product_id: str, 
        quantity_change: int, 
        reason: str
    ) -> None:
        self.inventory_logs.append({
            'product_id': product_id,
            'quantity_change': quantity_change,
            'reason': reason,
            'timestamp': datetime.datetime.now()
        })
    
    def add_product(
        self, 
        product_id: str, 
        name: str, 
        price: float, 
        quantity: int, 
        category: str, 
        weight: float, 
        supplier_id: str
    ) -> Product:
        product = Product(
            product_id, name, price, quantity, category, weight, supplier_id
        )
        self.products[product_id] = product
        self.log_inventory_change(product_id, quantity, "initial_stock")
        return product
    
    def add_customer(
        self, 
        customer_id: str, 
        name: str, 
        email: str, 
        tier: str, 
        phone: str, 
        address: str, 
        loyalty_points: int = 0
    ) -> Customer:
        customer = Customer(
            customer_id, name, email, tier, phone, address, loyalty_points
        )
        self.customers[customer_id] = customer
        return customer
    
    def add_supplier(
        self, 
        supplier_id: str, 
        name: str, 
        email: str, 
        reliability: float
    ) -> Supplier:
        supplier = Supplier(supplier_id, name, email, reliability)
        self.suppliers[supplier_id] = supplier
        return supplier
    
    def add_promotion(
        self, 
        promo_id: str, 
        code: str, 
        discount_percent: float, 
        min_purchase: float, 
        valid_until: datetime.datetime, 
        category: str
    ) -> Promotion:
        promo = Promotion(
            promo_id, code, discount_percent, min_purchase, valid_until, category
        )
        self.promotions[code] = promo
        return promo
    
    def get_product(self, product_id: str) -> Optional[Product]:
        return self.products.get(product_id)
    
    def get_customer(self, customer_id: str) -> Optional[Customer]:
        return self.customers.get(customer_id)
    
    def get_supplier(self, supplier_id: str) -> Optional[Supplier]:
        return self.suppliers.get(supplier_id)
