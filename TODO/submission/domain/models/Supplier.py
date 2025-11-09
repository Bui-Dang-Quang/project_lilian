class Supplier:
    def __init__(
        self, 
        supplier_id: str, 
        name: str, 
        email: str, 
        reliability_score: float
    ) -> None:
        self.supplier_id: str = supplier_id
        self.name: str = name
        self.email: str = email # This would ideally be: email: Email (a ValueObject)
        self.reliability_score: float = reliability_score
