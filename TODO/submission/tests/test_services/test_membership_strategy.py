import unittest
from submission.domain.enums.membership_tier import MembershipTierEnum
from submission.services.pricing.strategies.membership_discount import (
    MembershipTier,
    SuspendedMembership,
    BronzeMembership,
    SilverMembership,
    GoldMembership
)

class TestMembershipTierEnum(unittest.TestCase):
    
    def test_enum_values(self):
        """Tests that the enum string values are correct."""
        self.assertEqual(MembershipTierEnum.SUSPENDED.value, "suspended")
        self.assertEqual(MembershipTierEnum.BRONZE.value, "bronze")
        self.assertEqual(MembershipTierEnum.SILVER.value, "silver")
        self.assertEqual(MembershipTierEnum.GOLD.value, "gold")

class TestSuspendedMembership(unittest.TestCase):
    
    def setUp(self):
        self.tier = SuspendedMembership()
        
    def test_get_name(self):
        self.assertEqual(self.tier.get_name(), "suspended")

    def test_get_tier(self):
        self.assertEqual(self.tier.get_tier(), MembershipTierEnum.SUSPENDED)
        
    def test_get_discount(self):
        self.assertEqual(self.tier.get_discount(), 0.0)

class TestBronzeMembership(unittest.TestCase):
    
    def setUp(self):
        self.tier = BronzeMembership()
        
    def test_get_name(self):
        self.assertEqual(self.tier.get_name(), "bronze")

    def test_get_tier(self):
        self.assertEqual(self.tier.get_tier(), MembershipTierEnum.BRONZE)
        
    def test_get_discount(self):
        self.assertEqual(self.tier.get_discount(), 0.03)

class TestSilverMembership(unittest.TestCase):
    
    def setUp(self):
        self.tier = SilverMembership()
        
    def test_get_name(self):
        self.assertEqual(self.tier.get_name(), "silver")

    def test_get_tier(self):
        self.assertEqual(self.tier.get_tier(), MembershipTierEnum.SILVER)
        
    def test_get_discount(self):
        self.assertEqual(self.tier.get_discount(), 0.07)

class TestGoldMembership(unittest.TestCase):
    
    def setUp(self):
        self.tier = GoldMembership()
        
    def test_get_name(self):
        self.assertEqual(self.tier.get_name(), "gold")

    def test_get_tier(self):
        self.assertEqual(self.tier.get_tier(), MembershipTierEnum.GOLD)
        
    def test_get_discount(self):
        self.assertEqual(self.tier.get_discount(), 0.15)

# if __name__ == "__main__":
#     unittest.main(argv=['first-arg-is-ignored'], exit=False)
