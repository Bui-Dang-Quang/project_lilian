import unittest
from unittest.mock import MagicMock

# --- Import classes to be tested ---
from submission.services.tax_service import TaxService
from submission.services.pricing.strategies.tax_strategy import (
    TaxStrategy,
    DefaultTaxStrategy,
    CaliforniaTaxStrategy,
    NewYorkTaxStrategy,
    TexasTaxStrategy
)

# --- Test the simple strategies ---
class TestTaxStrategies(unittest.TestCase):

    def test_default_strategy(self):
        strategy = DefaultTaxStrategy()
        self.assertEqual(strategy.get_rate(), 0.08)

    def test_california_strategy(self):
        strategy = CaliforniaTaxStrategy()
        self.assertEqual(strategy.get_rate(), 0.0725)

    def test_new_york_strategy(self):
        strategy = NewYorkTaxStrategy()
        self.assertEqual(strategy.get_rate(), 0.04)

    def test_texas_strategy(self):
        strategy = TexasTaxStrategy()
        self.assertEqual(strategy.get_rate(), 0.0625)

# --- Test the main service logic ---
class TestTaxService(unittest.TestCase):

    def setUp(self):
        """Set up the service and mock customers."""
        self.tax_service = TaxService()
        self.subtotal = 100.0  # Use a simple subtotal for easy math
        
        # Create mock customers with different addresses
        self.customer_ca = MagicMock(address="123 Main St, CA")
        self.customer_ny = MagicMock(address="456 Oak Ave, NY 10001")
        self.customer_tx = MagicMock(address="789 Pine Rd, TX")
        self.customer_fl = MagicMock(address="111 Palm Way, FL") # Should use default
        self.customer_no_address = MagicMock(address=None) # Should use default

    def test_calculate_tax_california(self):
        """Test CA tax rate (7.25%)."""
        tax = self.tax_service.calculate_tax(self.subtotal, self.customer_ca)
        self.assertAlmostEqual(tax, 7.25) # 100.0 * 0.0725

    def test_calculate_tax_new_york(self):
        """Test NY tax rate (4.0%)."""
        tax = self.tax_service.calculate_tax(self.subtotal, self.customer_ny)
        self.assertEqual(tax, 4.0) # 100.0 * 0.04

    def test_calculate_tax_texas(self):
        """Test TX tax rate (6.25%)."""
        tax = self.tax_service.calculate_tax(self.subtotal, self.customer_tx)
        self.assertEqual(tax, 6.25) # 100.0 * 0.0625

    def test_calculate_tax_default_state(self):
        """Test a non-listed state (Florida) falls back to default (8%)."""
        tax = self.tax_service.calculate_tax(self.subtotal, self.customer_fl)
        self.assertEqual(tax, 8.0) # 100.0 * 0.08

    def test_calculate_tax_no_address(self):
        """Test that a customer with no address falls back to default (8%)."""
        tax = self.tax_service.calculate_tax(self.subtotal, self.customer_no_address)
        self.assertEqual(tax, 8.0) # 100.0 * 0.08
