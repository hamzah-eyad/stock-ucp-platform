import json
import os
from datetime import datetime

# Directory to save audit logs
LOGS_DIR = "logs"

def create_product(symbol, price, currency="USD"):
    # Define a stock as a tradeable product in the UCP system
    return {
        "type": "PRODUCT",
        "symbol": symbol,
        "price": price,
        "currency": currency,
        "timestamp": datetime.now().isoformat()
    }

def create_order(buyer, symbol, quantity, price):
    # Create a buy/sell order in the UCP format
    return {
        "type": "ORDER",
        "order_id": f"ORD-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "buyer": buyer,
        "symbol": symbol,
        "quantity": quantity,
        "price": price,
        "total": round(quantity * price, 2),
        "status": "PENDING",
        "timestamp": datetime.now().isoformat()
    }

def validate_order(order):
    # Validate that the order has all required fields and valid values
    if not order.get("symbol"):
        return False, "Missing stock symbol"
    if order.get("quantity", 0) <= 0:
        return False, "Quantity must be greater than zero"
    if order.get("price", 0) <= 0:
        return False, "Price must be greater than zero"
    if not order.get("buyer"):
        return False, "Missing buyer information"
    return True, "Order is valid"

def process_order(order):
    # Run validation and update order status accordingly
    is_valid, message = validate_order(order)
    if is_valid:
        order["status"] = "APPROVED"
    else:
        order["status"] = "REJECTED"
        order["reason"] = message
    return order

def create_invoice(order):
    # Generate an invoice for an approved order
    if order["status"] != "APPROVED":
        return None
    return {
        "type": "INVOICE",
        "invoice_id": f"INV-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "order_id": order["order_id"],
        "buyer": order["buyer"],
        "symbol": order["symbol"],
        "quantity": order["quantity"],
        "total": order["total"],
        "currency": "USD",
        "status": "PAID",
        "timestamp": datetime.now().isoformat()
    }

def create_refund(invoice, reason):
    # Create a refund record for a given invoice
    return {
        "type": "REFUND",
        "refund_id": f"REF-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "invoice_id": invoice["invoice_id"],
        "buyer": invoice["buyer"],
        "symbol": invoice["symbol"],
        "total": invoice["total"],
        "reason": reason,
        "status": "REFUNDED",
        "timestamp": datetime.now().isoformat()
    }

def save_to_log(record):
    # Save any UCP record (order, invoice, refund) to the audit log
    os.makedirs(LOGS_DIR, exist_ok=True)
    log_file = os.path.join(LOGS_DIR, "audit_log.json")

    logs = []
    if os.path.exists(log_file):
        with open(log_file, "r") as f:
            logs = json.load(f)

    logs.append(record)

    with open(log_file, "w") as f:
        json.dump(logs, f, indent=2)

def get_logs():
    # Read and return all records from the audit log
    log_file = os.path.join(LOGS_DIR, "audit_log.json")
    if not os.path.exists(log_file):
        return []
    with open(log_file, "r") as f:
        return json.load(f)