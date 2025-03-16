from decimal import Decimal
from django.conf import settings
from django.shortcuts import get_object_or_404
from products.models import Product

def bag_contents(request):
    bag_items = []
    total = 0
    product_count = 0
    bag = request.session.get("bag", {})
    for item_id, item_quantity in bag.items():
        try:
            product = get_object_or_404(Product, pk=item_id)
            line_total = item_quantity * product.price
            total += line_total
            product_count += item_quantity
            bag_items.append({
                "product": product,
                "quantity": item_quantity,
                "line_total": line_total
            })
        except Product.DoesNotExist:
            continue
    if total < settings.FREE_DELIVERY_THRESHOLD:
        delivery = total * (Decimal(settings.STANDARD_DELIVERY_PERCENTAGE) / Decimal(100))
        free_delivery_delta = settings.FREE_DELIVERY_THRESHOLD - total
    else:
        delivery = Decimal("0.00")
        free_delivery_delta = Decimal("0.00")
    grand_total = total + delivery
    return {
        "bag_items": bag_items,
        "total": total,
        "product_count": product_count,
        "delivery": delivery,
        "free_delivery_delta": free_delivery_delta,
        "free_delivery_threshold": settings.FREE_DELIVERY_THRESHOLD,
        "grand_total": grand_total
    }
