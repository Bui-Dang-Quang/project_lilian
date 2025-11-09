from abc import ABC, abstractmethod

class TaxStrategy(ABC):
    """The 'Strategy' interface for all tax calculators."""
    @abstractmethod
    def get_rate(self) -> float:
        pass  # pragma: no cover

class DefaultTaxStrategy(TaxStrategy):
    """The default tax rate."""
    def get_rate(self) -> float:
        return 0.08

class CaliforniaTaxStrategy(TaxStrategy):
    """California-specific tax rate."""
    def get_rate(self) -> float:
        return 0.0725

class NewYorkTaxStrategy(TaxStrategy):
    """New York-specific tax rate."""
    def get_rate(self) -> float:
        return 0.04

class TexasTaxStrategy(TaxStrategy):
    """Texas-specific tax rate."""
    def get_rate(self) -> float:
        return 0.0625
