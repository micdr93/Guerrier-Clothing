from decimal import Decimal
from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import logging
from products.models import Product

logger = logging.getLogger(__name__)


def view_bag(request):
    bag = request.session.get("bag", {})
    cart = []
    cart_total = Decimal('0.00')
    product_count = 0

    for item_id, item_data in bag.items():
        product = get_object_or_404(Product, pk=item_id)
        if isinstance(item_data, int):
            subtotal = product.price * item_data
            cart_total += subtotal  # corrected arithmetic
            product_count += item_data
            cart.append({
                "product": product,
                "quantity": item_data,
                "subtotal": subtotal
            })
        else:
            for size, quantity in item_data.items():
                subtotal = product.price * quantity
                cart_total += subtotal
                product_count += quantity
                cart.append({
                    "product": product,
                    "quantity": quantity,
                    "size": size,
                    "subtotal": subtotal
                })

    # Determine delivery and free delivery delta
    if cart_total < settings.FREE_DELIVERY_THRESHOLD:
        delivery = settings.STANDARD_DELIVERY
        free_delivery_delta = settings.FREE_DELIVERY_THRESHOLD - cart_total
    else:
        delivery = Decimal('0.00')
        free_delivery_delta = Decimal('0.00')

    grand_total = cart_total + delivery

    context = {
        "cart": cart,
        "cart_total": cart_total,
        "product_count": product_count,
        "delivery": delivery,
        "free_delivery_delta": free_delivery_delta,
        "grand_total": grand_total,
    }
    return render(request, "bag/bag_home.html", context)


def add_to_bag(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    quantity = int(request.POST.get("quantity", 1))
    size = request.POST.get("product_size")
    redirect_url = request.POST.get("redirect_url", "/")
    bag = request.session.get("bag", {})
    product_id_str = str(product_id)

    if size:
        bag.setdefault(product_id_str, {}).setdefault(size, 0)
        bag[product_id_str][size] += quantity
    else:
        bag[product_id_str] = bag.get(product_id_str, 0) + quantity

    request.session["bag"] = bag
    request.session.modified = True

    messages.success(request, f"Added {product.name} to your bag")

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({"success": True, "product_name": product.name})

    return redirect(redirect_url)


def remove_from_bag(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    size = request.POST.get("product_size")
    bag = request.session.get("bag", {})
    product_id_str = str(product_id)

    if size:
        if product_id_str in bag and size in bag[product_id_str]:
            del bag[product_id_str][size]
            if not bag[product_id_str]:
                del bag[product_id_str]
            messages.success(request, f"Removed size {size} {product.name} from your bag")
    else:
        if product_id_str in bag:
            del bag[product_id_str]
            messages.success(request, f"Removed {product.name} from your bag")

    request.session["bag"] = bag
    request.session.modified = True

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({"success": True})

    return redirect(reverse("bag:view_bag"))


@csrf_exempt
def update_bag(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    quantity = int(request.POST.get("quantity", 1))
    size = request.POST.get("size")
    bag = request.session.get("bag", {})
    product_id_str = str(product_id)

    if quantity > 0:
        if size:
            if product_id_str in bag:
                bag[product_id_str][size] = quantity
            else:
                bag[product_id_str] = {size: quantity}
        else:
            bag[product_id_str] = quantity
        messages.success(request, f"Updated {product.name} quantity to {quantity}")
    else:
        if size:
            if product_id_str in bag and size in bag[product_id_str]:
                del bag[product_id_str][size]
                if not bag[product_id_str]:
                    del bag[product_id_str]
        else:
            bag.pop(product_id_str, None)
        messages.success(request, f"Removed {product.name} from your bag")

    request.session["bag"] = bag
    request.session.modified = True

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({"success": True})

    return redirect(reverse("bag:view_bag"))


def bag_contents(request):
    bag_items = []
    total = 0
    product_count = 0
    bag = request.session.get("bag", {})

    for item_id, item_data in bag.items():
        try:
            product = get_object_or_404(Product, pk=item_id)

            if isinstance(item_data, int):
                quantity = item_data
                total_price = product.price * quantity
                total += total_price
                product_count += quantity
                bag_items.append(
                    {
                        "product": product,
                        "quantity": quantity,
                        "total_price": total_price,
                    }
                )
            else:
                # Handle products with sizes
                for size, quantity in item_data.items():
                    total_price = product.price * quantity
                    total += total_price
                    product_count += quantity
                    bag_items.append(
                        {
                            "product": product,
                            "quantity": quantity,
                            "size": size,
                            "total_price": total_price,
                        }
                    )
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

    # Calculate grand total
    grand_total = total + delivery

    context = {
        "cart": bag_items,
        "cart_total": total,
        "product_count": product_count,
        "delivery": delivery,
        "free_delivery_delta": free_delivery_delta,
        "free_delivery_threshold": settings.FREE_DELIVERY_THRESHOLD,
        "grand_total": grand_total,
    }

    # Debug logging to verify calculations
    print(f"Cart items: {len(bag_items)}")
    print(f"Total: {total}")
    print(f"Delivery: {delivery}")
    print(f"Grand Total: {grand_total}")

    return context
