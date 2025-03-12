from decimal import Decimal
from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

from products.models import Product
from recommendations.utils import get_recommended_items


def bag_home(request):
    bag = request.session.get("bag", {})
    bag_items = []
    total = 0
    product_count = 0

    for item_id, item_data in bag.items():
        try:
            product = get_object_or_404(Product, pk=item_id)

            # Check if item_data is a dictionary (for products with sizes) or an integer
            if isinstance(item_data, int):
                quantity = item_data
                total_price = product.price * quantity
                total += total_price
                product_count += quantity
                bag_items.append(
                    {
                        "product": product,
                        "quantity": quantity,
                        "subtotal": total_price,
                    }
                )
            else:
                # Handle products with sizes
                for size, quantity in item_data.items():
                    if size != "DEFAULT":
                        total_price = product.price * quantity
                        total += total_price
                        product_count += quantity
                        bag_items.append(
                            {
                                "product": product,
                                "quantity": quantity,
                                "size": size,
                                "subtotal": total_price,
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

    recommended_items = get_recommended_items(
        Product.objects.filter(id__in=[int(id) for id in bag.keys() if id.isdigit()])
    )

    context = {
        "cart": bag_items,
        "cart_total": total,
        "product_count": product_count,
        "delivery": delivery,
        "free_delivery_delta": free_delivery_delta,
        "free_delivery_threshold": settings.FREE_DELIVERY_THRESHOLD,
        "grand_total": grand_total,
        "recommended_items": recommended_items,
    }
    return render(request, "bag/bag_home.html", context)


def view_bag(request):
    return render(request, "bag/bag_home.html")


def add_to_bag(request, product_id):
    """Add a specified product to the shopping bag"""

    product = get_object_or_404(Product, pk=product_id)
    quantity = int(request.POST.get("quantity", 1))
    redirect_url = request.POST.get("redirect_url", reverse("products:products"))
    size = None

    if "product_size" in request.POST:
        size = request.POST.get("product_size")

    bag = request.session.get("bag", {})
    product_id_str = str(product_id)

    if size:
        if product_id_str in bag:
            if isinstance(bag[product_id_str], dict):
                if size in bag[product_id_str]:
                    bag[product_id_str][size] += quantity
                else:
                    bag[product_id_str][size] = quantity
            else:
                # Convert to dict for sizes
                current_quantity = bag[product_id_str]
                bag[product_id_str] = {"DEFAULT": current_quantity, size: quantity}
        else:
            bag[product_id_str] = {size: quantity}
    else:
        if product_id_str in bag:
            if isinstance(bag[product_id_str], dict):
                if "DEFAULT" in bag[product_id_str]:
                    bag[product_id_str]["DEFAULT"] += quantity
                else:
                    bag[product_id_str]["DEFAULT"] = quantity
            else:
                bag[product_id_str] = bag[product_id_str] + quantity
        else:
            bag[product_id_str] = quantity

    request.session["bag"] = bag

    # Debug
    print(f"Updated bag: {bag}")

    # If AJAX request
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse(
            {
                "success": True,
                "product_name": product.name,
            }
        )

    messages.success(request, f"Added {product.name} to your bag")
    return redirect(redirect_url)


@csrf_exempt
def remove_from_bag(request, product_id):
    """Remove the item from the shopping bag"""
    try:
        product = get_object_or_404(Product, pk=product_id)
        bag = request.session.get("bag", {})
        product_id_str = str(product_id)
        size = None

        if "size" in request.POST:
            size = request.POST.get("size")

        if size:
            if product_id_str in bag and isinstance(bag[product_id_str], dict):
                if size in bag[product_id_str]:
                    del bag[product_id_str][size]
                    if not bag[product_id_str]:
                        del bag[product_id_str]
                    messages.success(
                        request, f"Removed size {size} {product.name} from your bag"
                    )
            else:
                messages.error(request, f"Error removing item: size {size} not found")
        else:
            if product_id_str in bag:
                del bag[product_id_str]
                messages.success(request, f"Removed {product.name} from your bag")
            else:
                messages.error(request, f"Error removing item: product not in bag")

        request.session["bag"] = bag

        # Debug
        print(f"Updated bag after removal: {bag}")

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"success": True})

        return redirect(reverse("bag:view_bag"))

    except Exception as e:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"error": str(e)}, status=500)

        messages.error(request, f"Error removing item: {e}")
        return redirect(reverse("bag:view_bag"))


@csrf_exempt
def update_bag(request, product_id):
    """Update the quantity of the specified product to the specified amount"""
    try:
        product = get_object_or_404(Product, pk=product_id)
        quantity = int(request.POST.get("quantity", 1))
        size = None
        if "size" in request.POST:
            size = request.POST.get("size")

        bag = request.session.get("bag", {})
        product_id_str = str(product_id)

        if quantity > 0:
            if size:
                if product_id_str in bag:
                    if isinstance(bag[product_id_str], dict):
                        bag[product_id_str][size] = quantity
                    else:
                        # Convert to dict for sizes
                        bag[product_id_str] = {size: quantity}
                else:
                    bag[product_id_str] = {size: quantity}
            else:
                if product_id_str in bag and isinstance(bag[product_id_str], dict):
                    if "DEFAULT" in bag[product_id_str]:
                        bag[product_id_str]["DEFAULT"] = quantity
                    else:
                        # Just update the first size we find if DEFAULT not present
                        first_size = next(iter(bag[product_id_str]))
                        bag[product_id_str][first_size] = quantity
                else:
                    bag[product_id_str] = quantity

            messages.success(request, f"Updated {product.name} quantity to {quantity}")
        else:
            if size:
                if product_id_str in bag and isinstance(bag[product_id_str], dict):
                    if size in bag[product_id_str]:
                        del bag[product_id_str][size]
                        if not bag[product_id_str]:
                            del bag[product_id_str]
            else:
                if product_id_str in bag:
                    del bag[product_id_str]

            messages.success(request, f"Removed {product.name} from your bag")

        request.session["bag"] = bag

        # Debug
        print(f"Updated bag after quantity update: {bag}")

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"success": True})

        return redirect(reverse("bag:view_bag"))
    except Exception as e:
        messages.error(request, f"Error updating bag: {e}")
        return redirect(reverse("bag:view_bag"))
