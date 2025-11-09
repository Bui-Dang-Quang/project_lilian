import unittest
from submission.services.pricing.strategies.bulk_discount import (
    BulkDiscount,
    NoBulkDiscount,
    FiveItemsDiscount,
    TenItemsDiscount
)

class TestNoBulkDiscount(unittest.TestCase):
    
    def setUp(self):
        self.strategy = NoBulkDiscount()
        
    def test_get_discount(self):
        self.assertEqual(self.strategy.get_discount(), 0.0)
        
    def test_get_min_quantity(self):
        self.assertEqual(self.strategy.get_min_quantity(), 0)

class TestFiveItemsDiscount(unittest.TestCase):
    
    def setUp(self):
        self.strategy = FiveItemsDiscount()
        
    def test_get_discount(self):
        self.assertEqual(self.strategy.get_discount(), 0.02)
        
    def test_get_min_quantity(self):
        self.assertEqual(self.strategy.get_min_quantity(), 5)

class TestTenItemsDiscount(unittest.TestCase):
    
    def setUp(self):
        self.strategy = TenItemsDiscount()
        
    def test_get_discount(self):
        self.assertEqual(self.strategy.get_discount(), 0.05)
        
    def test_get_min_quantity(self):
        self.assertEqual(self.strategy.get_min_quantity(), 10)

# if __name__ == "__main__":
#     unittest.main(argv=['first-arg-is-ignored'], exit=False)
