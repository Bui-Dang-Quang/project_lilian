from abc import ABC, abstractmethod
import datetime
from typing import Dict, List, Any, Tuple, Optional

# --- Import Dependencies ---
from submission.repositories.in_memory.DataStore import DataStore
from submission.services.customer_service import CustomerInterface
from submission.domain.models.Order import Order
from submission.domain.models.Product import Product
from submission.domain.enums.order_status import OrderStatus

# --- Type Alias for the Report Structure ---
ReportDict = Dict[str, Any]

class ReportingInterface(ABC):
    
    @abstractmethod
    def generate_sales_report(
        self, 
        start_date: datetime.datetime, 
        end_date: datetime.datetime
    ) -> ReportDict:
        """
        Generates a summary report of sales, products, and customers
        within a given date range.
        """
        pass  # pragma: no cover

class ReportingService(ReportingInterface):
    def __init__(self, data_store: DataStore, customer_service: CustomerInterface) -> None:
        self.data_store: DataStore = data_store
        self.customer_service: CustomerInterface = customer_service

    def generate_sales_report(
        self, 
        start_date: datetime.datetime, 
        end_date: datetime.datetime
    ) -> ReportDict:
        """
        Generates a summary report of sales, products, and customers.
        This replaces the global function.
        """
        report: ReportDict = {
            'total_sales': 0.0,
            'total_orders': 0,
            'cancelled_orders': 0,
            'products_sold': {},
            'revenue_by_category': {},
            'top_customers': []
        }

        # Iterate through orders in the DataStore
        for order in self.data_store.orders.values():
            if start_date <= order.created_at <= end_date:
                if order.status != OrderStatus.CANCELLED:
                    report['total_sales'] += order.total_price
                    report['total_orders'] += 1

                    for item in order.items:
                        product: Optional[Product] = self.data_store.get_product(item.product_id)
                        if product:
                            # Tally products sold
                            if product.product_id not in report['products_sold']:
                                report['products_sold'][product.product_id] = 0
                            report['products_sold'][product.product_id] += item.quantity

                            # Tally revenue by category
                            if product.category not in report['revenue_by_category']:
                                report['revenue_by_category'][product.category] = 0.0
                            report['revenue_by_category'][product.category] += item.quantity * item.unit_price
                else:
                    report['cancelled_orders'] += 1

        # Find top customers
        customer_spending: Dict[str, float] = {}
        customer_id: str
        for customer_id in self.data_store.customers.keys():
            ltv: float = self.customer_service.get_customer_lifetime_value(customer_id)
            customer_spending[customer_id] = ltv

        # A List of Tuples, e.g., [('c1', 500.0), ('c2', 300.0)]
        sorted_customers: List[Tuple[str, float]] = sorted(
            customer_spending.items(), 
            key=lambda item: item[1], 
            reverse=True
        )
        report['top_customers'] = sorted_customers[:10]

        return report
