from abc import ABC, abstractmethod
from typing import List, Optional

# --- Import Dependencies ---
# (We assume these files exist in their respective locations)
from submission.repositories.in_memory.DataStore import DataStore
from submission.services.supplier_service import SupplierInterface
from submission.domain.models.Order import Order
from submission.domain.models.OrderItem import OrderItem
from submission.domain.models.Product import Product


class InventoryInterface(ABC):
    
    @abstractmethod
    def deduct_stock_and_log(self, order_items: List[OrderItem], order: Order) -> None:
        pass  # pragma: no cover

    @abstractmethod
    def check_and_notify_low_stock(self, order_items: List[OrderItem]) -> None:
        """
        Checks items for low stock and triggers supplier
        notifications if the threshold is met.
        """
        pass  # pragma: no cover

    @abstractmethod
    def restore_stock(self, order: Order) -> None:
        pass  # pragma: no cover

    @abstractmethod
    def restock_product(self, product_id: str, quantity: int, supplier_id: Optional[str] = None) -> bool:
        pass  # pragma: no cover

    @abstractmethod
    def get_low_stock_products(self, threshold: int = 10) -> List[Product]:
        pass  # pragma: no cover

    @abstractmethod
    def check_stock_availability(self, order_items: List[OrderItem]) -> bool:
        pass  # pragma: no cover

class InventoryService(InventoryInterface):
    def __init__(self, data_store: DataStore, supplier_service: SupplierInterface) -> None:
        self.data_store: DataStore = data_store
        self.supplier_service: SupplierInterface = supplier_service

    def deduct_stock_and_log(self, order_items: List[OrderItem], order: Order) -> None:
        for item in order_items:
            product: Optional[Product] = self.data_store.get_product(item.product_id)
            if product:
                product.quantity_available -= item.quantity
                self.data_store.log_inventory_change(
                    item.product_id, 
                    -item.quantity, 
                    f"order_{order.order_id}"
                )
                
    def check_and_notify_low_stock(self, order_items: List[OrderItem]) -> None:
        for item in order_items:
            product: Optional[Product] = self.data_store.get_product(item.product_id)
            
            # Low stock threshold
            if product and product.quantity_available < 5:
                self.supplier_service.notify_supplier_reorder(product)


    def restore_stock(self, order: Order) -> None:
        for item in order.items:
            product: Optional[Product] = self.data_store.get_product(item.product_id)
            if product:
                product.quantity_available += item.quantity

                self.data_store.log_inventory_change(
                    item.product_id, 
                    item.quantity, 
                    f"cancel_order_{order.order_id}"
                )

    def restock_product(self, product_id: str, quantity: int, supplier_id: Optional[str] = None) -> bool:
        product: Optional[Product] = self.data_store.get_product(product_id)
        if not product:
            print("Product not found")
            return False
        
        if supplier_id and product.supplier_id != supplier_id:
            print("Supplier mismatch")
            return False

        product.quantity_available += quantity
        self.data_store.log_inventory_change(
            product_id, 
            quantity, 
            "restock"
        )
        print(f"Restocked {product.name} by {quantity}. New stock: {product.quantity_available}")
        return True
    
    def get_low_stock_products(self, threshold: int = 10) -> List[Product]:
        
        low_stock: List[Product] = []
        for product in self.data_store.products.values():
            if product.quantity_available <= threshold:
                low_stock.append(product)

        return low_stock
    
    def check_stock_availability(self, order_items: List[OrderItem]) -> bool:
        """
        Checks if all items in an order are in stock.
        """
        for item in order_items:
            product: Optional[Product] = self.data_store.get_product(item.product_id)
            if not product:
                print(f"Order FAILED: Product {item.product_id} not found.")
                return False
            if product.quantity_available < item.quantity:
                print(f"Order FAILED: Not enough stock for {product.name} (Available: {product.quantity_available}, Requested: {item.quantity}).")
                return False
        return True # All items are in stock
