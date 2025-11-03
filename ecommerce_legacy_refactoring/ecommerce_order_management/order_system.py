# Legacy E-Commerce Order System
# WARNING: This is legacy code that needs major refactoring!
# Tasks: Apply SOLID principles, add unit tests, add type checking with mypy

import datetime
import json
import random

class Product:
    def __init__(self, product_id, name, price, quantity_available, category, weight, supplier_id):
        self.product_id = product_id
        self.name = name
        self.price = price
        self.quantity_available = quantity_available
        self.category = category
        self.weight = weight
        self.supplier_id = supplier_id
        self.discount_eligible = True

class Customer:
    def __init__(self, customer_id, name, email, membership_tier, phone, address, loyalty_points):
        self.customer_id = customer_id
        self.name = name
        self.email = email
        self.membership_tier = membership_tier
        self.phone = phone
        self.address = address
        self.loyalty_points = loyalty_points
        self.order_history = []

class OrderItem:
    def __init__(self, product_id, quantity, unit_price):
        self.product_id = product_id
        self.quantity = quantity
        self.unit_price = unit_price
        self.discount_applied = 0

class Order:
    def __init__(self, order_id, customer_id, items, status, created_at, total_price, shipping_cost):
        self.order_id = order_id
        self.customer_id = customer_id
        self.items = items
        self.status = status
        self.created_at = created_at
        self.total_price = total_price
        self.shipping_cost = shipping_cost
        self.tracking_number = None
        self.payment_method = None

class Supplier:
    def __init__(self, supplier_id, name, email, reliability_score):
        self.supplier_id = supplier_id
        self.name = name
        self.email = email
        self.reliability_score = reliability_score

class Promotion:
    def __init__(self, promo_id, code, discount_percent, min_purchase, valid_until, category):
        self.promo_id = promo_id
        self.code = code
        self.discount_percent = discount_percent
        self.min_purchase = min_purchase
        self.valid_until = valid_until
        self.category = category
        self.used_count = 0

# Global storage (bad practice!)
products = {}
customers = {}
orders = {}
suppliers = {}
promotions = {}
shipments = {}
inventory_logs = []
next_order_id = 1
next_shipment_id = 1

def add_product(product_id, name, price, quantity, category, weight, supplier_id):
    products[product_id] = Product(product_id, name, price, quantity, category, weight, supplier_id)
    log_inventory_change(product_id, quantity, "initial_stock")

def add_customer(customer_id, name, email, tier, phone, address):
    customers[customer_id] = Customer(customer_id, name, email, tier, phone, address, 0)

def add_supplier(supplier_id, name, email, reliability):
    suppliers[supplier_id] = Supplier(supplier_id, name, email, reliability)

def add_promotion(promo_id, code, discount, min_purchase, valid_until, category):
    promotions[code] = Promotion(promo_id, code, discount, min_purchase, valid_until, category)

def get_product(product_id):
    return products.get(product_id)

def get_customer(customer_id):
    return customers.get(customer_id)

def get_supplier(supplier_id):
    return suppliers.get(supplier_id)

def log_inventory_change(product_id, quantity_change, reason):
    inventory_logs.append({
        'product_id': product_id,
        'quantity_change': quantity_change,
        'reason': reason,
        'timestamp': datetime.datetime.now()
    })

# Giant monolithic function doing everything (violates SRP, OCP, DIP)
def process_order(customer_id, order_items, payment_info, promo_code=None, shipping_method='standard'):
    global next_order_id

    # Check customer exists
    customer = customers.get(customer_id)
    if not customer:
        print("Customer not found")
        return None

    # Validate customer membership is active
    if customer.membership_tier == 'suspended':
        print("Customer account is suspended")
        return None

    # Check all products available
    for item in order_items:
        product = products.get(item.product_id)
        if not product:
            print(f"Product {item.product_id} not found")
            return None
        if product.quantity_available < item.quantity:
            print(f"Not enough stock for {product.name}")
            return None

    # Calculate subtotal
    subtotal = 0
    total_weight = 0
    for item in order_items:
        product = products[item.product_id]
        subtotal += item.quantity * item.unit_price
        total_weight += product.weight * item.quantity

    # Apply membership discount (hardcoded logic)
    membership_discount = 0
    if customer.membership_tier == 'gold':
        membership_discount = 0.15
    elif customer.membership_tier == 'silver':
        membership_discount = 0.07
    elif customer.membership_tier == 'bronze':
        membership_discount = 0.03

    subtotal_after_membership = subtotal * (1 - membership_discount)

    # Apply promotional code discount
    promo_discount = 0
    if promo_code:
        promo = promotions.get(promo_code)
        if promo:
            if datetime.datetime.now() < promo.valid_until:
                if subtotal >= promo.min_purchase:
                    # Check if any items match promo category
                    applicable = False
                    for item in order_items:
                        product = products[item.product_id]
                        if promo.category == 'all' or product.category == promo.category:
                            applicable = True
                            break
                    if applicable:
                        promo_discount = promo.discount_percent / 100
                        promo.used_count += 1

    subtotal_after_promo = subtotal_after_membership * (1 - promo_discount)

    # Apply bulk discount (another hardcoded rule)
    bulk_discount = 0
    total_items = sum(item.quantity for item in order_items)
    if total_items >= 10:
        bulk_discount = 0.05
    elif total_items >= 5:
        bulk_discount = 0.02

    subtotal_after_bulk = subtotal_after_promo * (1 - bulk_discount)

    # Calculate loyalty points discount
    loyalty_discount = 0
    if customer.loyalty_points >= 100:
        loyalty_discount = min(subtotal_after_bulk * 0.1, customer.loyalty_points * 0.01)
        customer.loyalty_points -= int(loyalty_discount * 100)

    subtotal_after_loyalty = subtotal_after_bulk - loyalty_discount

    # Calculate shipping cost (complex logic)
    shipping_cost = 0
    if shipping_method == 'express':
        shipping_cost = 25 + (total_weight * 0.5)
        if customer.membership_tier == 'gold':
            shipping_cost *= 0.5
    elif shipping_method == 'standard':
        if subtotal_after_loyalty < 50:
            shipping_cost = 5 + (total_weight * 0.2)
        else:
            shipping_cost = 0  # Free shipping over $50
    elif shipping_method == 'overnight':
        shipping_cost = 50 + (total_weight * 1.0)

    # Calculate tax (different rates for different states - hardcoded)
    tax_rate = 0.08  # Default
    if hasattr(customer, 'address') and customer.address:
        if 'CA' in customer.address:
            tax_rate = 0.0725
        elif 'NY' in customer.address:
            tax_rate = 0.04
        elif 'TX' in customer.address:
            tax_rate = 0.0625

    tax = subtotal_after_loyalty * tax_rate

    total = subtotal_after_loyalty + shipping_cost + tax

    # Process payment (fake validation)
    if not payment_info.get("valid"):
        print("Payment failed - invalid payment info")
        return None

    if payment_info.get("type") == "credit_card":
        if len(payment_info.get("card_number", "")) < 16:
            print("Invalid card number")
            return None
    elif payment_info.get("type") == "paypal":
        if not payment_info.get("email"):
            print("PayPal email required")
            return None

    # Check payment amount
    if payment_info.get("amount", 0) < total:
        print("Insufficient payment amount")
        return None

    # Deduct stock and log
    for item in order_items:
        product = products[item.product_id]
        product.quantity_available -= item.quantity
        log_inventory_change(item.product_id, -item.quantity, f"order_{next_order_id}")

    # Create order
    order_id = next_order_id
    next_order_id += 1
    order = Order(
        order_id=order_id,
        customer_id=customer_id,
        items=order_items,
        status='pending',
        created_at=datetime.datetime.now(),
        total_price=total,
        shipping_cost=shipping_cost
    )
    order.payment_method = payment_info.get("type")
    orders[order_id] = order

    # Update customer history
    customer.order_history.append(order_id)

    # Award loyalty points (1 point per dollar spent)
    customer.loyalty_points += int(subtotal)

    # Send notification (hardcoded, not testable)
    print(f"To: {customer.email}: Order {order_id} confirmed! Total: ${total:.2f}")
    if customer.phone:
        print(f"SMS to {customer.phone}: Order {order_id} confirmed")

    # Check if we need to reorder from supplier
    for item in order_items:
        product = products[item.product_id]
        if product.quantity_available < 5:  # Low stock threshold
            notify_supplier_reorder(product.product_id, product.supplier_id)

    return order

def notify_supplier_reorder(product_id, supplier_id):
    product = products.get(product_id)
    supplier = suppliers.get(supplier_id)
    if product and supplier:
        print(f"Email to {supplier.email}: Low stock alert for {product.name}")

def get_order(order_id):
    return orders.get(order_id)

def update_order_status(order_id, new_status):
    order = orders.get(order_id)
    if not order:
        return None

    old_status = order.status
    order.status = new_status

    customer = customers.get(order.customer_id)
    if customer:
        print(f"To: {customer.email}: Order {order_id} status changed to {new_status}")

    # If shipped, create tracking
    if new_status == 'shipped' and not order.tracking_number:
        order.tracking_number = f"TRACK{order_id}{random.randint(1000, 9999)}"
        create_shipment(order_id, order.tracking_number)

    return order

def create_shipment(order_id, tracking_number):
    global next_shipment_id
    shipment_id = next_shipment_id
    next_shipment_id += 1
    shipments[shipment_id] = {
        'shipment_id': shipment_id,
        'order_id': order_id,
        'tracking_number': tracking_number,
        'created_at': datetime.datetime.now(),
        'status': 'in_transit'
    }
    return shipments[shipment_id]

def apply_additional_discount(order_id, discount_percent, reason):
    order = orders.get(order_id)
    if not order:
        return None
    if order.status != 'pending':
        print("Can only apply discount to pending orders")
        return None
    order.total_price = order.total_price * (1 - discount_percent / 100)
    print(f"Applied {discount_percent}% discount to order {order_id}. Reason: {reason}")
    return order

def cancel_order(order_id, reason):
    order = orders.get(order_id)
    if not order:
        print("Order not found")
        return False

    if order.status in ['shipped', 'delivered']:
        print(f"Cannot cancel order in {order.status} status")
        return False

    # Restore stock
    for item in order.items:
        product = products.get(item.product_id)
        if product:
            product.quantity_available += item.quantity
            log_inventory_change(item.product_id, item.quantity, f"cancel_order_{order_id}")

    order.status = 'cancelled'

    customer = customers.get(order.customer_id)
    if customer:
        print(f"To: {customer.email}: Order {order_id} has been cancelled. Reason: {reason}")
        # Refund loyalty points that were used
        # (This is simplified - in reality would need to track points used)

    return True

def get_customer_orders(customer_id):
    customer_orders = []
    for order in orders.values():
        if order.customer_id == customer_id:
            customer_orders.append(order)
    return customer_orders

def restock_product(product_id, quantity, supplier_id=None):
    product = products.get(product_id)
    if not product:
        print("Product not found")
        return False

    # Verify supplier if provided
    if supplier_id and product.supplier_id != supplier_id:
        print("Supplier mismatch")
        return False

    product.quantity_available += quantity
    log_inventory_change(product_id, quantity, "restock")
    print(f"Restocked {product.name} by {quantity}. New stock: {product.quantity_available}")
    return True

def update_product_price(product_id, new_price):
    product = products.get(product_id)
    if not product:
        return False
    old_price = product.price
    product.price = new_price
    print(f"Updated {product.name} price from ${old_price:.2f} to ${new_price:.2f}")
    return True

def get_low_stock_products(threshold=10):
    low_stock = []
    for product in products.values():
        if product.quantity_available <= threshold:
            low_stock.append(product)
    return low_stock

def get_customer_lifetime_value(customer_id):
    customer = customers.get(customer_id)
    if not customer:
        return 0

    total_value = 0
    for order_id in customer.order_history:
        order = orders.get(order_id)
        if order and order.status != 'cancelled':
            total_value += order.total_price

    return total_value

def upgrade_customer_membership(customer_id):
    customer = customers.get(customer_id)
    if not customer:
        return False

    lifetime_value = get_customer_lifetime_value(customer_id)

    # Hardcoded upgrade rules
    if lifetime_value >= 1000 and customer.membership_tier != 'gold':
        customer.membership_tier = 'gold'
        print(f"Customer {customer.name} upgraded to Gold!")
        return True
    elif lifetime_value >= 500 and customer.membership_tier == 'standard':
        customer.membership_tier = 'silver'
        print(f"Customer {customer.name} upgraded to Silver!")
        return True
    elif lifetime_value >= 200 and customer.membership_tier == 'standard':
        customer.membership_tier = 'bronze'
        print(f"Customer {customer.name} upgraded to Bronze!")
        return True

    return False

def generate_sales_report(start_date, end_date):
    # Giant function that does everything (bad!)
    report = {
        'total_sales': 0,
        'total_orders': 0,
        'cancelled_orders': 0,
        'products_sold': {},
        'revenue_by_category': {},
        'top_customers': []
    }

    for order in orders.values():
        if start_date <= order.created_at <= end_date:
            if order.status != 'cancelled':
                report['total_sales'] += order.total_price
                report['total_orders'] += 1

                for item in order.items:
                    product = products.get(item.product_id)
                    if product:
                        if product.product_id not in report['products_sold']:
                            report['products_sold'][product.product_id] = 0
                        report['products_sold'][product.product_id] += item.quantity

                        if product.category not in report['revenue_by_category']:
                            report['revenue_by_category'][product.category] = 0
                        report['revenue_by_category'][product.category] += item.quantity * item.unit_price
            else:
                report['cancelled_orders'] += 1

    # Find top customers
    customer_spending = {}
    for customer_id, customer in customers.items():
        customer_spending[customer_id] = get_customer_lifetime_value(customer_id)

    sorted_customers = sorted(customer_spending.items(), key=lambda x: x[1], reverse=True)
    report['top_customers'] = sorted_customers[:10]

    return report

def send_marketing_email(customer_segment, message):
    # Another function mixing concerns
    count = 0
    for customer in customers.values():
        send = False

        if customer_segment == 'all':
            send = True
        elif customer_segment == 'gold' and customer.membership_tier == 'gold':
            send = True
        elif customer_segment == 'inactive':
            # Check if customer has ordered in last 90 days
            has_recent_order = False
            cutoff = datetime.datetime.now() - datetime.timedelta(days=90)
            for order_id in customer.order_history:
                order = orders.get(order_id)
                if order and order.created_at > cutoff:
                    has_recent_order = True
                    break
            if not has_recent_order:
                send = True

        if send:
            print(f"Email to {customer.email}: {message}")
            count += 1

    return count
