import datetime
from typing import List, Optional

from submission.repositories.in_memory.DataStore import DataStore
from submission.domain.models.  OrderItem import OrderItem
from submission.domain.models.Customer import Customer
from submission.domain.models.Product import Product
from submission.domain.models.Promotion import Promotion
from submission.services.pricing.strategies.bulk_discount import BulkDiscount


class PricingService:
    def __init__(self, order_items: List[OrderItem], data_store: DataStore) -> None:
        self.order_items: List[OrderItem] = order_items
        self.data_store: DataStore = data_store

        self.subtotal: float = self._calculate_subtotal(order_items, data_store)
        self.discounted_price: float = self.subtotal
        
        # Track applied discount amounts
        self.promotion_discount_amount: float = 0.0
        self.bulk_discount_amount: float = 0.0
        self.membership_discount_amount: float = 0.0
        self.loyalty_discount_amount: float = 0.0
    
    def _calculate_subtotal(self, order_items: List[OrderItem], data_store: DataStore) -> float:
        """Private helper to calculate base subtotal."""
        subtotal: float = 0.0
        for item in order_items:
            product: Optional[Product] = data_store.get_product(item.product_id)
            if product:
                subtotal += item.quantity * item.unit_price
        return subtotal
    
    def apply_membership_discount(self, customer: Customer) -> "PricingService":
        """Applies membership discount. Returns self for chaining."""
        discount_rate: float = customer.membership_tier.get_discount()

        if discount_rate > 0:
            self.membership_discount_amount = self.discounted_price * discount_rate
            self.discounted_price -= self.membership_discount_amount
        
        return self
    
    def apply_promotion_discount(self, promotion_code: Optional[str]) -> "PricingService":
        """Applies promo code discount. Returns self for chaining."""
        if not promotion_code:
            return self
        
        promo: Optional[Promotion] = self.data_store.promotions.get(promotion_code)

        if not promo:
            return self
        
        if datetime.datetime.now() >= promo.valid_until:
            print("Promotion has expired.")
            return self
        
        if self.discounted_price < promo.min_purchase:
            print("Promotion is not applicable.")
            return self
        
        applicable: bool = False
        if promo.category == "all":
            applicable = True
        else:
            for item in self.order_items:
                product: Optional[Product] = self.data_store.get_product(item.product_id)
                if product and product.category == promo.category:
                    applicable = True
                    break
        
        if applicable:
            promo_discount_rate: float = promo.discount_percent / 100
            self.promotion_discount_amount = self.discounted_price * promo_discount_rate
            self.discounted_price -= self.promotion_discount_amount
            promo.used_count += 1
            print(f"Promotion {promo.code} applied.")
        else:
            print("Promotion is not applicable.")
        
        return self
    
    def apply_bulk_discount(self, available_discounts: List[BulkDiscount]) -> "PricingService":
        """Applies the best matching bulk discount. Returns self for chaining."""
        total_items: int = sum(item.quantity for item in self.order_items)
        
        qualified_discounts: List[BulkDiscount] = [
            strategy for strategy in available_discounts 
            if total_items >= strategy.get_min_quantity()
        ]

        # Assumes 'NoBulkDiscount' is always in the list, so qualified_discounts is never empty
        best_discount_strategy: BulkDiscount = sorted(
            qualified_discounts, 
            key=lambda d: d.get_min_quantity(), 
            reverse=True
        )[0]

        bulk_discount_rate: float = best_discount_strategy.get_discount()
        
        if bulk_discount_rate > 0:
            self.bulk_discount_amount = self.discounted_price * bulk_discount_rate 
            self.discounted_price -= self.bulk_discount_amount
            print(f"Applied bulk discount: {bulk_discount_rate*100}%")
            
        return self

    def apply_loyalty_discount(self, customer: Customer) -> "PricingService":
        """Applies loyalty discount. Returns self for chaining."""
        if customer.loyalty_points >= 100:
            max_discount_from_price: float = self.discounted_price * 0.1
            max_discount_from_points: float = customer.loyalty_points * 0.01

            loyalty_discount: float = min(max_discount_from_price, max_discount_from_points)

            self.loyalty_discount_amount = loyalty_discount
            self.discounted_price -= self.loyalty_discount_amount
            
            customer.loyalty_points -= int(loyalty_discount * 100)
            
            print(f"Applied loyalty discount: ${loyalty_discount:.2f}")
        else:
            print("Not enough loyalty points to apply discount.")
        
        return self

    def get_final_discounted_price(self) -> float:
        """Returns the final price after all discounts."""
        return self.discounted_price
