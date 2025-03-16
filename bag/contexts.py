from decimal import Decimal
from django.conf import settings
from django.shortcuts import get_object_or_404
from products.models import Product

def bag_contents(request):
    bag_items = []
    total = 0
    product_count = 0
    bag = request.session.get("bag", {})

    for item_id, item_data in bag.items():
        try:
            product = get_object_or_404(Product, pk=item_id)
            if isinstance(item_data, int):
                # When item_data is a simple quantity
                quantity = item_data
                line_total = product.price * quantity
                total += line_total
                product_count += quantity
                bag_items.append({
                    "product": product,
                    "quantity": quantity,
                    "line_total": line_total,
                })
            else:
                # When item_data is a dict (i.e., items with sizes)
                for size, quantity in item_data.items():
                    line_total = product.price * quantity
                    total += line_total
                    product_count += quantity
                    bag_items.append({
                        "product": product,
                        "quantity": quantity,
                        "size": size,
                        "line_total": line_total,
                    })
        except Exception as e:
            print(f"Error processing item {item_id}: {e}")
            continue

    # Calculate delivery cost
    if total < settings.FREE_DELIVERY_THRESHOLD:
        delivery = total * Decimal(settings.STANDARD_DELIVERY_PERCENTAGE / 100)
        free_delivery_delta = settings.FREE_DELIVERY_THRESHOLD - total
    else:
        delivery = Decimal(0)
        free_delivery_delta = Decimal(0)

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