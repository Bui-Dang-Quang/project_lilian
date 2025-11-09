# Use relative imports to get the strategy and enum
from submission.services.pricing.strategies.membership_discount import(
    MembershipTier,
    BronzeMembership,
    SilverMembership,
    GoldMembership,
    SuspendedMembership
)
from typing import List

class Customer:
    def __init__(
        self, 
        customer_id: str, 
        name: str, 
        email: str, 
        membership_tier_str: str,  # Renamed this parameter for clarity
        phone: str, 
        address: str, 
        loyalty_points: int
    ) -> None:
        
        self.customer_id: str = customer_id
        self.name: str = name
        self.email: str = email
        self.phone: str = phone
        self.address: str = address
        self.loyalty_points: int = loyalty_points
        
        # This attribute holds the actual strategy *object*
        self.membership_tier: MembershipTier = self._get_membership_tier_from_string(membership_tier_str)
        
        # order_history will hold integers (the order IDs)
        self.order_history: List[int] = [] 

    def _get_membership_tier_from_string(self, tier_str: str) -> MembershipTier:
        if tier_str == "bronze":
            return BronzeMembership()
        elif tier_str == "silver":
            return SilverMembership()
        elif tier_str == "gold":
            return GoldMembership()
        else:
            # Defaults to suspended if the string is unknown (e.g., "standard")
            return SuspendedMembership()
