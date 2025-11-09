import unittest
from unittest.mock import Mock, MagicMock  # <-- Import MagicMock

# Import the classes to be tested
from submission.services.shipping_service import (
    ShippingStrategy,
    ExpressShipping,
    StandardShipping,
    OvernightShipping
)

class TestStandardShipping(unittest.TestCase):
    
    def setUp(self):
        self.strategy = StandardShipping()
        self.mock_customer = MagicMock() # <-- Use MagicMock
        self.weight = 10.0

    def test_cost_below_50(self):
        """Test cost when subtotal is less than $50."""
        subtotal = 49.99
        cost = self.strategy.cal_shipping_cost(self.weight, self.mock_customer, subtotal)
        self.assertEqual(cost, 7.0)

    def test_cost_at_or_above_50(self):
        """Test cost when subtotal is $50 (free shipping)."""
        subtotal = 50.0
        cost = self.strategy.cal_shipping_cost(self.weight, self.mock_customer, subtotal)
        self.assertEqual(cost, 0.0)

class TestExpressShipping(unittest.TestCase):

    def setUp(self):
        self.strategy = ExpressShipping()
        self.weight = 10.0
        self.subtotal = 100.0 # Subtotal doesn't matter for this strategy

    def test_cost_non_gold_member(self):
        """Test cost for a non-gold member."""
        mock_customer = MagicMock() # <-- Use MagicMock
        mock_customer.membership_tier.get_name.return_value = "silver"
        
        cost = self.strategy.cal_shipping_cost(self.weight, mock_customer, self.subtotal)
        self.assertEqual(cost, 30.0)

    def test_cost_gold_member(self):
        """Test 50% discount for a gold member."""
        mock_customer = MagicMock() # <-- Use MagicMock
        mock_customer.membership_tier.get_name.return_value = "gold"
        
        cost = self.strategy.cal_shipping_cost(self.weight, mock_customer, self.subtotal)
        self.assertEqual(cost, 15.0)

class TestOvernightShipping(unittest.TestCase):
    
    def test_cost_calculation(self):
        """Test the overnight calculation."""
        strategy = OvernightShipping()
        mock_customer = MagicMock() # <-- Use MagicMock
        subtotal = 100.0
        weight = 10.0
        
        cost = strategy.cal_shipping_cost(weight, mock_customer, subtotal)
        self.assertEqual(cost, 60.0)

# (You can remove the __main__ block if you are using discover)
