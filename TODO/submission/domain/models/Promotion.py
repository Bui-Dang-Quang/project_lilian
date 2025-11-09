import datetime
class Promotion:
    def __init__(
        self, 
        promo_id: str, 
        code: str, 
        discount_percent: float, 
        min_purchase: float, 
        valid_until: datetime.datetime, 
        category: str
    ) -> None:
        self.promo_id: str = promo_id
        self.code: str = code
        self.discount_percent: float = discount_percent
        self.min_purchase: float = min_purchase
        self.valid_until: datetime.datetime = valid_until
        self.category: str = category
        self.used_count: int = 0
