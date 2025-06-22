from django.shortcuts import render, redirect, reverse, HttpResponse, get_object_or_404
from django.contrib import messages
from products.models import Product
from decimal import Decimal
from django.conf import settings

def view_bag(request):
    bag = request.session.get("bag", {})
    cart = []
    cart_total = Decimal('0.00')
    product_count = 0

    for item_id, item_data in bag.items():
        product = get_object_or_404(Product, pk=item_id)
        # Check if item_data is an integer
        if isinstance(item_data, int):
            quantity = item_data
            subtotal = product.price * quantity
            cart_total += subtotal 
            product_count += quantity
            cart.append({
                "product": product,
                "quantity": quantity,
                "subtotal": subtotal
            })
        # Otherwise, if it's a dict, process based on its keys.
        elif isinstance(item_data, dict):
            if "quantity" in item_data:
                quantity = item_data["quantity"]
                subtotal = product.price * quantity
                cart_total += subtotal 
                product_count += quantity
                cart.append({
                    "product": product,
                    "quantity": quantity,
                    "subtotal": subtotal
                })
            elif "items_by_size" in item_data:
                for size, quantity in item_data["items_by_size"].items():
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
        # Compute delivery as a percentage of cart total
        delivery = (cart_total * settings.STANDARD_DELIVERY_PERCENTAGE) / Decimal('100')
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
    product_id = str(product_id)
    quantity_str = request.POST.get("quantity", "")
    if not quantity_str:
        messages.error(request, 'Quantity must be specified')
        return redirect(request.POST.get("redirect_url", reverse("home")))
    try:
        quantity = int(quantity_str)
    except ValueError:
        messages.error(request, 'Invalid quantity provided')
        return redirect(request.POST.get("redirect_url", reverse("home")))
    redirect_url = request.POST.get('redirect_url') or reverse("home")
    size = request.POST.get('product_size', None)
    bag = request.session.get('bag', {})
    if size:
        if product_id in bag and isinstance(bag[product_id], dict) and bag[product_id].get('items_by_size') is not None:
            if size in bag[product_id]['items_by_size']:
                bag[product_id]['items_by_size'][size] += quantity
                messages.success(request, f'Updated size {size.upper()} {product.name} quantity to {bag[product_id]["items_by_size"][size]}')
            else:
                bag[product_id]['items_by_size'][size] = quantity
                messages.success(request, f'Added size {size.upper()} {product.name} to your bag')
        else:
            bag[product_id] = {'items_by_size': {size: quantity}}
            messages.success(request, f'Added size {size.upper()} {product.name} to your bag')
    else:
        if product_id in bag:
            if isinstance(bag[product_id], dict) and 'quantity' in bag[product_id]:
                bag[product_id]['quantity'] += quantity
                messages.success(request, f'Updated {product.name} quantity to {bag[product_id]["quantity"]}')
            elif isinstance(bag[product_id], int):
                bag[product_id] += quantity
                messages.success(request, f'Updated {product.name} quantity to {bag[product_id]}')
            else:
                bag[product_id] = {'quantity': quantity}
                messages.success(request, f'Added {product.name} to your bag')
        else:
            bag[product_id] = {'quantity': quantity}
            messages.success(request, f'Added {product.name} to your bag')
    request.session['bag'] = bag
    return redirect(redirect_url)

def adjust_bag(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    product_id = str(product_id)
    quantity = int(request.POST.get('quantity'))
    size = request.POST.get('product_size', None)
    bag = request.session.get('bag', {})
    if size:
        if quantity > 0:
            bag[product_id]['items_by_size'][size] = quantity
            messages.success(request, f'Updated size {size.upper()} {product.name} quantity to {bag[product_id]["items_by_size"][size]}')
        else:
            del bag[product_id]['items_by_size'][size]
            if not bag[product_id]['items_by_size']:
                bag.pop(product_id)
            messages.success(request, f'Removed size {size.upper()} {product.name} from your bag')
    else:
        if quantity > 0:
            if isinstance(bag[product_id], dict) and 'quantity' in bag[product_id]:
                bag[product_id]['quantity'] = quantity
            else:
                bag[product_id] = {'quantity': quantity}
            messages.success(request, f'Updated {product.name} quantity to {bag[product_id]["quantity"]}')
        else:
            bag.pop(product_id)
            messages.success(request, f'Removed {product.name} from your bag')
    request.session['bag'] = bag
    return redirect(reverse('bag:view_bag'))

def remove_from_bag(request, product_id):
    try:
        product = get_object_or_404(Product, pk=product_id)
        product_id = str(product_id)
        size = request.POST.get('product_size', None)
        bag = request.session.get('bag', {})
        if size:
            del bag[product_id]['items_by_size'][size]
            if not bag[product_id]['items_by_size']:
                bag.pop(product_id)
            messages.success(request, f'Removed size {size.upper()} {product.name} from your bag')
        else:
            bag.pop(product_id)
            messages.success(request, f'Removed {product.name} from your bag')
        request.session['bag'] = bag
        return redirect(reverse('bag:view_bag'))
    except Exception as e:
        messages.error(request, f'Error removing item: {e}')
        return redirect(reverse('bag:view_bag'))
