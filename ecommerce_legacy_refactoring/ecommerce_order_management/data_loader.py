# Utility to load/save data (also needs refactoring!)
import json
import datetime
from order_system import *

def save_data_to_file(filename):
    # Another monolithic function doing too much
    data = {
        'products': {},
        'customers': {},
        'orders': {},
        'suppliers': {},
        'promotions': {}
    }

    # Convert products
    for pid, product in products.items():
        data['products'][pid] = {
            'product_id': product.product_id,
            'name': product.name,
            'price': product.price,
            'quantity_available': product.quantity_available,
            'category': product.category,
            'weight': product.weight,
            'supplier_id': product.supplier_id
        }

    # Convert customers
    for cid, customer in customers.items():
        data['customers'][cid] = {
            'customer_id': customer.customer_id,
            'name': customer.name,
            'email': customer.email,
            'membership_tier': customer.membership_tier,
            'phone': customer.phone,
            'address': customer.address,
            'loyalty_points': customer.loyalty_points,
            'order_history': customer.order_history
        }

    # Convert orders (simplified)
    for oid, order in orders.items():
        data['orders'][oid] = {
            'order_id': order.order_id,
            'customer_id': order.customer_id,
            'status': order.status,
            'created_at': order.created_at.isoformat(),
            'total_price': order.total_price
        }

    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"Data saved to {filename}")

def load_data_from_file(filename):
    # Load data (also monolithic)
    try:
        with open(filename, 'r') as f:
            data = json.load(f)

        # Load products
        for pid, pdata in data.get('products', {}).items():
            add_product(
                pdata['product_id'],
                pdata['name'],
                pdata['price'],
                pdata['quantity_available'],
                pdata['category'],
                pdata['weight'],
                pdata['supplier_id']
            )

        # Load customers
        for cid, cdata in data.get('customers', {}).items():
            add_customer(
                cdata['customer_id'],
                cdata['name'],
                cdata['email'],
                cdata['membership_tier'],
                cdata['phone'],
                cdata['address']
            )
            customer = customers[cdata['customer_id']]
            customer.loyalty_points = cdata['loyalty_points']
            customer.order_history = cdata['order_history']

        print(f"Data loaded from {filename}")
        return True
    except FileNotFoundError:
        print(f"File {filename} not found")
        return False
    except Exception as e:
        print(f"Error loading data: {e}")
        return False
