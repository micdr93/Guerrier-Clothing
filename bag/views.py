from django.shortcuts import render, redirect, reverse, HttpResponse, get_object_or_404
from django.contrib import messages
from products.models import Product

def view_bag(request):
    bag = request.session.get('bag', {})
    return render(request, 'bag/bag.html', {'cart': bag})

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
        return HttpResponse(status=200)
    except Exception as e:
        messages.error(request, f'Error removing item: {e}')
        return HttpResponse(status=500)
