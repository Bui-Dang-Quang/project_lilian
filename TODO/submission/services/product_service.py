from abc import ABC, abstractmethod
from typing import Optional

# --- Import Dependencies ---
from submission.repositories.in_memory.DataStore import DataStore
from submission.domain.models.Product import Product

class ProductInterface(ABC):
    
    @abstractmethod
    def update_product_price(self, product_id: str, new_price: float) -> bool:
        """
        Updates the price of a product.
        """
        pass  # pragma: no cover

class ProductService(ProductInterface):
    def __init__(self, data_store: DataStore) -> None:
        self.data_store: DataStore = data_store

    def update_product_price(self, product_id: str, new_price: float) -> bool:
        """
        Updates the price of a product.
        This replaces the global function.
        """
        
        # Get product from the DataStore
        product: Optional[Product] = self.data_store.get_product(product_id)
        
        if not product:
            return False
            
        old_price: float = product.price
        product.price = new_price
        
        print(f"Updated {product.name} price from ${old_price:.2f} to ${new_price:.2f}")
        return True
