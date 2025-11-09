from abc import ABC, abstractmethod
from typing import Optional

# Import the dependencies
from submission.repositories.in_memory.DataStore import DataStore
from submission.domain.models.Product import Product
from submission.domain.models.Supplier import Supplier

class SupplierInterface(ABC):
    """
    Interface for the Supplier Service, defining communication contracts.
    """
    @abstractmethod
    def notify_supplier_reorder(self, product: Product) -> None:
        """
        Notifies a supplier about a low-stock product.
        """
        pass  # pragma: no cover

class SupplierService(SupplierInterface):
    """
    Implements the logic for handling supplier communications.
    """
    def __init__(self, data_store: DataStore) -> None:
        self.data_store: DataStore = data_store

    def notify_supplier_reorder(self, product: Product) -> None:
        """
        Finds the supplier for a product and sends a
        low-stock alert.
        """
        # DataStore.get_supplier returns Optional[Supplier]
        supplier: Optional[Supplier] = self.data_store.get_supplier(product.supplier_id)
        
        if supplier:
            print(f"Email to {supplier.email}: Low stock alert for {product.name}")
        else:
            print(f"Warning: No supplier found for product {product.product_id}")
