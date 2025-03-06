from decimal import Decimal
from django.conf import settings
from django.shortcuts import get_object_or_404
from products.models import Product

def bag_contents(request):
    """
    Context processor for bag contents
    """
    bag_items = []
    total = 0
    product_count = 0
    bag = request.session.get('bag', {})

    print(f"Session Bag: {bag}")  # Debugging

    for item_id, item_quantity in bag.items():
        try:
            product = get_object_or_404(Product, pk=item_id)
            line_total = item_quantity * product.price
            total += line_total
            product_count += item_quantity
            bag_items.append({
                'product': product,
                'quantity': item_quantity,
                'line_total': line_total,
                'total_price': line_total,  # Add for compatibility
            })
        except Product.DoesNotExist:
            continue

    print(f"Total Price in Bag Context: {total}")  # Debugging

    grand_total = total  # If using delivery costs, add them here.

    return {
        'bag_items': bag_items,
        'cart': bag_items,  # Added cart as an alias for bag_items
        'total': total,
        'cart_total': total,  # Added cart_total as an alias for total
        'product_count': product_count,
        'grand_total': grand_total,
    }