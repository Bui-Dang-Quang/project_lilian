from abc import ABC, abstractmethod
from submission.domain.enums.membership_tier import MembershipTierEnum
class MembershipTier(ABC):
    def __init__(self, membership_tier: MembershipTierEnum , discount: float) -> None:
        self.membership_tier = membership_tier
        self.discount = discount
    
    @abstractmethod
    def get_name(self) -> str:
        pass  # pragma: no cover

    @abstractmethod
    def get_tier(self) -> MembershipTierEnum:
        pass  # pragma: no cover
    
    @abstractmethod
    def get_discount(self) -> float:
        pass  # pragma: no cover

class SuspendedMembership(MembershipTier):
    def __init__(self) -> None:
        super().__init__(MembershipTierEnum.SUSPENDED, 0.0)

    def get_name(self) -> str:
        return self.membership_tier.value

    def get_tier(self) -> MembershipTierEnum:
        return self.membership_tier

    def get_discount(self) -> float:
        return self.discount
    
class BronzeMembership(MembershipTier):
    def __init__(self) -> None:
        super().__init__(MembershipTierEnum.BRONZE, 0.03)

    def get_name(self) -> str:
        return self.membership_tier.value

    def get_tier(self) -> MembershipTierEnum:
        return self.membership_tier

    def get_discount(self) -> float:
        return self.discount

class SilverMembership(MembershipTier):
    def __init__(self) -> None:
        super().__init__(MembershipTierEnum.SILVER, 0.07)

    def get_name(self) -> str:
        return self.membership_tier.value

    def get_tier(self) -> MembershipTierEnum:
        return self.membership_tier

    def get_discount(self) -> float:
        return self.discount

class GoldMembership(MembershipTier):
    def __init__(self) -> None:
        super().__init__(MembershipTierEnum.GOLD, 0.15)

    def get_name(self) -> str:
        return self.membership_tier.value
    
    def get_tier(self) -> MembershipTierEnum:
        return self.membership_tier

    def get_discount(self) -> float:
        return self.discount
