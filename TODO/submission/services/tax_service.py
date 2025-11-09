from typing import Dict, Optional
from submission.domain.models.Customer import Customer
from submission.services.pricing.strategies.tax_strategy import (
    TaxStrategy,
    DefaultTaxStrategy,
    CaliforniaTaxStrategy,
    NewYorkTaxStrategy,
    TexasTaxStrategy
)

class TaxService:
    """
    Selects the correct tax strategy based on address
    and calculates the tax.
    """
    def __init__(self) -> None:
        # We can pre-load our strategies
        self.strategies: Dict[str, TaxStrategy] = {
            'CA': CaliforniaTaxStrategy(),
            'NY': NewYorkTaxStrategy(),
            'TX': TexasTaxStrategy()
        }
        self.default_strategy: TaxStrategy = DefaultTaxStrategy()

    def _get_strategy(self, address: Optional[str]) -> TaxStrategy:
        """
        This is the logic from your 'if/elif' block,
        refactored to return a strategy object.
        """
        if not address:
            return self.default_strategy
            
        if 'CA' in address:
            return self.strategies['CA']
        elif 'NY' in address:
            return self.strategies['NY']
        elif 'TX' in address:
            return self.strategies['TX']
        else:
            return self.default_strategy


    def calculate_tax(self, subtotal: float, customer: Customer) -> float:
        """
        The main public method to calculate tax.
        """
        # 1. Get the correct strategy
        strategy: TaxStrategy = self._get_strategy(customer.address)
        
        # 2. Get the rate from that strategy
        tax_rate: float = strategy.get_rate()
        
        # 3. Calculate the tax
        tax: float = subtotal * tax_rate
        return tax
