from abc import ABC, abstractmethod
class BulkDiscount(ABC):
    def __init__(self, min_quantity: int, discount: float) -> None:
        self.min_quantity = min_quantity
        self.discount = discount
    
    @abstractmethod
    def get_discount(self) -> float:
        pass # pragma: no cover
    
    @abstractmethod
    def get_min_quantity(self) -> int:
        pass # pragma: no cover

class NoBulkDiscount(BulkDiscount):
    def __init__(self) -> None:
        super().__init__(0, 0.0)

    def get_discount(self) -> float:
        return self.discount
    
    def get_min_quantity(self) -> int:
        return self.min_quantity

class TenItemsDiscount(BulkDiscount):
    def __init__(self) -> None:
        super().__init__(10, 0.05)

    def get_discount(self) -> float:
        return self.discount
    
    def get_min_quantity(self) -> int:
        return self.min_quantity
    
class FiveItemsDiscount(BulkDiscount):
    def __init__(self) -> None:
        super().__init__(5, 0.02)

    def get_discount(self) -> float:
        return self.discount
    
    def get_min_quantity(self) -> int:
        return self.min_quantity
