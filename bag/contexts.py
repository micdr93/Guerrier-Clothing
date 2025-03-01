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

    print(f"Session Bag: {bag}")  # ✅ Debugging

    for item_id, quantity in bag.items():
        try:
            product = get_object_or_404(Product, pk=item_id)
            total += quantity * product.price
            product_count += quantity
            bag_items.append({
                'item_id': item_id,
                'quantity': quantity,
                'product': product,
            })
        except Product.DoesNotExist:
            continue

    print(f"Total Price in Bag Context: {total}")  # ✅ Debugging

    grand_total = total  # If using delivery costs, add them here.

    return {
        'bag_items': bag_items,
        'total': total,
        'product_count': product_count,
        'grand_total': grand_total,
    }