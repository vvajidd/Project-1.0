total = 0
grandTotal = 0

def total(cart_items):
    total = 0
    quantity = 0
    for item in cart_items:
        total += (item.product.price * item.quantity)
        quantity += item.quantity
    return total

def quantity(cart_item):
    quantity = 0
    total = 0
    for item in cart_item:
        total += (item.product.price * item.quantity)
        quantity += item.quantity
    return quantity

def tax(total):
    return (.06 * total)

def grand_total(total, tax):
    return total + tax
