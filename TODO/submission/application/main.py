import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

# --- Import DataStore ---
from submission.repositories.in_memory.DataStore import DataStore

# --- Import Domain Models & Enums ---
from submission.domain.models.OrderItem import OrderItem
from submission.domain.models.Customer import Customer
from submission.domain.models.Product import Product
from submission.domain.models.Order import Order
from submission.domain.enums.order_status import OrderStatus

# --- Import All Strategies ---
from submission.services.pricing.strategies.bulk_discount import (
    NoBulkDiscount, 
    FiveItemsDiscount, 
    TenItemsDiscount,
    BulkDiscount
)

# --- Import All Service Interfaces & Implementations ---
from submission.services.supplier_service import SupplierService, SupplierInterface
from submission.services.inventory_service import InventoryService, InventoryInterface
from submission.services.customer_service import CustomerService, CustomerInterface
from submission.services.notification_service import NotificationService, NotificationInterface
from submission.services.shipping_service import ShippingService, ShippingServiceInterface
from submission.services.order_service import OrderService, OrderInterface
from submission.services.payment_service import PaymentService, PaymentServiceInterface
from submission.services.tax_service import TaxService
from submission.services.product_service import ProductService, ProductInterface
from submission.services.reporting_service import ReportingService, ReportingInterface
from submission.services.pricing.PricingService import PricingService

@dataclass
class ServiceContainer:
    """
    A simple container to hold and manage the dependencies of all services.
    This uses Dependency Injection to wire up the application.
    """
    db: DataStore
    
    # Services are initialized in order of dependency
    supplier: SupplierInterface
    inventory: InventoryInterface
    customer: CustomerInterface
    notification: NotificationInterface
    shipping: ShippingServiceInterface
    order: OrderInterface
    payment: PaymentServiceInterface
    tax: TaxService
    product: ProductInterface
    reporting: ReportingInterface

    # Available bulk discount strategies
    bulk_discount_strategies: List[BulkDiscount]

    @staticmethod
    def initialize() -> "ServiceContainer":
        """Factory method to create and wire all services."""
        db = DataStore()
        
        # Initialize individual services
        supplier_service = SupplierService(db)
        inventory_service = InventoryService(db, supplier_service)
        customer_service = CustomerService(db)
        notification_service = NotificationService() # No dependencies
        shipping_service = ShippingService(db)
        order_service = OrderService(
            db, 
            notification_service, 
            shipping_service, 
            inventory_service, 
            customer_service
        )
        payment_service = PaymentService() # No dependencies
        tax_service = TaxService() # No dependencies
        product_service = ProductService(db)
        reporting_service = ReportingService(db, customer_service)

        # Bulk strategies for the pricing service
        bulk_strategies = [NoBulkDiscount(), FiveItemsDiscount(), TenItemsDiscount()]

        return ServiceContainer(
            db=db,
            supplier=supplier_service,
            inventory=inventory_service,
            customer=customer_service,
            notification=notification_service,
            shipping=shipping_service,
            order=order_service,
            payment=payment_service,
            tax=tax_service,
            product=product_service,
            reporting=reporting_service,
            bulk_discount_strategies=bulk_strategies
        )

def setup_data(db: DataStore):
    """Populates the in-memory DataStore with sample data."""
    print("--- 1. Setting up sample data ---")
    
    # Suppliers
    db.add_supplier("S1", "TechSupplier", "sales@techsupplier.com", 0.95)
    db.add_supplier("S2", "BookWorld", "orders@bookworld.com", 0.99)

    # Products
    db.add_product("P1", "Laptop", 1200.00, 10, "electronics", 2.5, "S1")
    db.add_product("P2", "Mouse", 25.00, 3, "electronics", 0.2, "S1") # Low stock
    db.add_product("P3", "Python Book", 45.00, 20, "books", 0.8, "S2")
    db.add_product("P4", "Headphones", 150.00, 15, "electronics", 0.5, "S1")

    # Customers
    db.add_customer("C1", "Alice Smith", "alice@example.com", "gold", "555-1234", "123 Main St, CA", 500)
    db.add_customer("C2", "Bob Johnson", "bob@example.com", "bronze", "555-5678", "456 Oak Ave, NY", 50)
    db.add_customer("C3", "Charlie Lee", "charlie@example.com", "silver", "555-9012", "789 Pine Ln, TX", 200)

    # Promotions
    db.add_promotion(
        "PR1", 
        "HOLIDAY10", 
        10.0, 
        50.0, 
        datetime.datetime.now() + datetime.timedelta(days=30), 
        "all"
    )
    db.add_promotion(
        "PR2", 
        "BOOKSALE", 
        15.0, 
        40.0, 
        datetime.datetime.now() + datetime.timedelta(days=10), 
        "books"
    )
    print("--- Data setup complete ---\n")

def place_order_facade(
    services: ServiceContainer,
    customer_id: str,
    item_requests: List[Dict[str, Any]], # e.g., [{"product_id": "P1", "quantity": 1}]
    shipping_method: str,
    payment_info: Dict[str, Any],
    promo_code: Optional[str] = None
) -> Optional[Order]:
    """
    A Facade function that coordinates all services to process an order.
    """
    print(f"--- [START] Processing Order for Customer {customer_id} ---")
    try:
        # 1. Get Customer
        customer = services.db.get_customer(customer_id)
        if not customer:
            print(f"Order FAILED: Customer {customer_id} not found.")
            return None
        print(f"Customer '{customer.name}' (Tier: {customer.membership_tier.get_name()}) found.")

        # 2. Create OrderItem objects and check product existence
        order_items: List[OrderItem] = []
        total_weight: float = 0.0
        for item_req in item_requests:
            product = services.db.get_product(item_req["product_id"])
            if not product:
                print(f"Order FAILED: Product {item_req['product_id']} not found.")
                return None
            
            order_items.append(OrderItem(
                product_id=product.product_id,
                quantity=item_req["quantity"],
                unit_price=product.price
            ))
            total_weight += product.weight * item_req["quantity"]
        
        # 3. Check Stock Availability
        if not services.inventory.check_stock_availability(order_items):
            # Error message is printed by the service
            return None
        print("Stock available for all items.")

        # 4. Calculate Pricing
        price_calc = PricingService(order_items, services.db)
        
        # --- Apply all discounts ---
        (
            price_calc
            .apply_bulk_discount(services.bulk_discount_strategies)
            .apply_membership_discount(customer)
            .apply_promotion_discount(promo_code)
            .apply_loyalty_discount(customer) # Note: This spends points
        )
        
        discounted_subtotal = price_calc.get_final_discounted_price()
        print(f"Subtotal: ${price_calc.subtotal:.2f}")
        print(f"Discounted Subtotal: ${discounted_subtotal:.2f}")

        # 5. Calculate Tax
        tax = services.tax.calculate_tax(discounted_subtotal, customer)
        print(f"Tax: ${tax:.2f}")

        # 6. Calculate Shipping
        shipping_cost = services.shipping.shipping_cost(
            shipping_method, 
            total_weight, 
            customer, 
            discounted_subtotal
        )
        print(f"Shipping ({shipping_method}): ${shipping_cost:.2f}")

        # 7. Final Total
        total_price = discounted_subtotal + tax + shipping_cost
        print(f"TOTAL PRICE: ${total_price:.2f}")

        # 8. Validate Payment
        is_valid, msg = services.payment.validate_payment(payment_info, total_price)
        if not is_valid:
            print(f"Order FAILED: Payment validation failed. Reason: {msg}")
            # Note: In a real app, you might need to refund loyalty points
            return None
        print("Payment successful.")

        # 9. Create Order (in PENDING status)
        order = services.order.create_order(
            customer_id=customer_id,
            order_items=order_items,
            total_price=total_price,
            shipping_cost=shipping_cost,
            payment_method=payment_info.get("type", "unknown")
        )
        print(f"Order {order.order_id} created in PENDING status.")

        # 10. Post-Order Finalization
        # - Deduct stock
        services.inventory.deduct_stock_and_log(order_items, order)
        print(f"Stock deducted for order {order.order_id}.")
        
        # - Send confirmation
        services.notification.send_order_confirmation(customer, order)
        
        # - Update customer history & loyalty
        services.customer.finalize_customer_order_updates(customer, order.order_id, price_calc.subtotal)
        print(f"Customer {customer.customer_id} history and loyalty points updated.")
        
        # - Check for low stock
        services.inventory.check_and_notify_low_stock(order_items)
        
        # - Check for membership upgrade
        services.customer.check_and_upgrade_membership(customer_id)

        print(f"--- [SUCCESS] Order {order.order_id} Processed ---")
        return order

    except Exception as e:
        print(f"--- [ERROR] Order processing failed: {e} ---")
        return None


def main():
    """
    Main function to initialize services and run simulations.
    """
    # Initialize the database and all services
    services = ServiceContainer.initialize()
    setup_data(services.db)

    # --- SIMULATION 1: Successful Order (Alice) ---
    # Alice (Gold) buys a Laptop and 5 Headphones.
    # This should trigger the 5-item bulk discount.
    print("\n--- SIMULATION 1: Successful Order (Alice) ---")
    items_1 = [
        {"product_id": "P1", "quantity": 1}, # Laptop
        {"product_id": "P4", "quantity": 5}  # Headphones (Total 6 items)
    ]
    payment_1 = {
        "type": "credit_card", 
        "card_number": "1234567812345678", 
        "amount": 2500.0, 
        "valid": True
    }
    order_1 = place_order_facade(
        services=services,
        customer_id="C1",
        item_requests=items_1,
        shipping_method="express",
        payment_info=payment_1,
        promo_code="HOLIDAY10"
    )

    # --- SIMULATION 2: Low Stock Trigger (Bob) ---
    # Bob (Bronze) buys 2 Mouses. Stock is 3, so it will fall to 1.
    # This should trigger the low-stock notification.
    print("\n--- SIMULATION 2: Low Stock Order (Bob) ---")
    items_2 = [
        {"product_id": "P2", "quantity": 2} # Mouse
    ]
    payment_2 = {
        "type": "paypal", 
        "email": "bob@example.com",
        "amount": 100.0, 
        "valid": True
    }
    order_2 = place_order_facade(
        services=services,
        customer_id="C2",
        item_requests=items_2,
        shipping_method="standard",
        payment_info=payment_2
    )
    
    # Check stock of P2
    p2 = services.db.get_product("P2")
    print(f"Current stock of {p2.name}: {p2.quantity_available}") # Should be 1

    # --- SIMULATION 3: Failed Order (Insufficient Stock) ---
    # Charlie (Silver) tries to buy 2 Mouses. Only 1 is left.
    print("\n--- SIMULATION 3: Failed Order (Stock) ---")
    items_3 = [
        {"product_id": "P2", "quantity": 2} # Mouse
    ]
    payment_3 = {
        "type": "credit_card", 
        "card_number": "8765432187654321", 
        "amount": 100.0, 
        "valid": True
    }
    order_3 = place_order_facade(
        services=services,
        customer_id="C3",
        item_requests=items_3,
        shipping_method="standard",
        payment_info=payment_3
    )

    # --- SIMULATION 4: Admin Tasks ---
    print("\n--- SIMULATION 4: Admin Tasks ---")
    
    # Ship Alice's order
    if order_1:
        print(f"Shipping order {order_1.order_id}...")
        services.order.update_order_status(order_1.order_id, OrderStatus.SHIPPED)
        print(f"Order {order_1.order_id} status: {order_1.status.value}, Tracking: {order_1.tracking_number}")

    # Cancel Bob's order
    if order_2:
        print(f"Cancelling order {order_2.order_id}...")
        services.order.cancel_order(order_2.order_id, "Customer request")
        print(f"Order {order_2.order_id} status: {order_2.status.value}")
        # Stock for P2 should be restored (1 + 2 = 3)
        print(f"Current stock of {p2.name}: {p2.quantity_available}") # Should be 3
    
    # Restock Mouse
    print("Restocking Mouse (P2)...")
    services.inventory.restock_product("P2", 20) # Now 23

    # --- SIMULATION 5: Reporting ---
    print("\n--- SIMULATION 5: Generating Report ---")
    start_date = datetime.datetime.now() - datetime.timedelta(days=1)
    end_date = datetime.datetime.now() + datetime.timedelta(days=1)
    
    report = services.reporting.generate_sales_report(start_date, end_date)
    
    import json
    print(json.dumps(report, indent=2, default=str))


if __name__ == "__main__":
    main()
