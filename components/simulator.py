from components.ucp_engine import (
    create_product, create_order, 
    process_order, create_invoice, 
    create_refund, save_to_log
)

def merchant_offer(symbol, price, currency="USD"):
    # Merchant lists a stock as an available product for trading
    product = create_product(symbol, price, currency)
    save_to_log(product)
    return product

def buyer_request(buyer_name, symbol, quantity, price):
    # Buyer submits a purchase order for a given stock
    order = create_order(buyer_name, symbol, quantity, price)
    processed = process_order(order)
    save_to_log(processed)

    # If order is approved, generate an invoice
    if processed["status"] == "APPROVED":
        invoice = create_invoice(processed)
        save_to_log(invoice)
        return processed, invoice

    return processed, None

def request_refund(invoice, reason="Customer requested refund"):
    # Process a refund request for a given invoice
    if not invoice:
        return None
    refund = create_refund(invoice, reason)
    save_to_log(refund)
    return refund

def run_simulation(symbol, price, quantity=10, buyer="SimulatedBuyer"):
    # Run a full simulation: offer → order → invoice
    print(f"\n--- Starting UCP Simulation for {symbol} ---")

    # Step 1: Merchant lists the stock
    product = merchant_offer(symbol, price)
    print(f"[MERCHANT] Listed {symbol} at ${price}")

    # Step 2: Buyer places an order
    order, invoice = buyer_request(buyer, symbol, quantity, price)
    print(f"[BUYER] Order status: {order['status']}")

    # Step 3: Show invoice if approved
    if invoice:
        print(f"[INVOICE] {invoice['invoice_id']} - Total: ${invoice['total']}")
    else:
        print(f"[REJECTED] Reason: {order.get('reason', 'Unknown')}")

    return order, invoice