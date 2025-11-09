class Product:
    def __init__(
        self, 
        product_id: str, 
        name: str, 
        price: float, 
        quantity_available: int, 
        category: str, 
        weight: float, 
        supplier_id: str
    ) -> None:
        
        self.product_id: str = product_id
        self.name: str = name
        self.price: float = price
        self.quantity_available: int = quantity_available
        self.category: str = category
        self.weight: float = weight
        self.supplier_id: str = supplier_id
        self.discount_eligible: bool = True
