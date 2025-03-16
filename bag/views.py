from django.shortcuts import render, redirect, reverse, HttpResponse, get_object_or_404
from django.contrib import messages
from products.models import Product
import logging

logger = logging.getLogger(__name__)

def view_bag(request):
    return render(request, 'bag/bag.html')

def add_to_bag(request, item_id):
    try:
        product = get_object_or_404(Product, pk=item_id)
        item_id = str(item_id)
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
            if item_id in bag and isinstance(bag[item_id], dict) and bag[item_id].get('items_by_size') is not None:
                if size in bag[item_id]['items_by_size']:
                    bag[item_id]['items_by_size'][size] += quantity
                    messages.success(request, f'Updated size {size.upper()} {product.name} quantity to {bag[item_id]["items_by_size"][size]}')
                else:
                    bag[item_id]['items_by_size'][size] = quantity
                    messages.success(request, f'Added size {size.upper()} {product.name} to your bag')
            else:
                bag[item_id] = {'items_by_size': {size: quantity}}
                messages.success(request, f'Added size {size.upper()} {product.name} to your bag')
        else:
            if item_id in bag:
                if isinstance(bag[item_id], dict) and 'quantity' in bag[item_id]:
                    bag[item_id]['quantity'] += quantity
                    messages.success(request, f'Updated {product.name} quantity to {bag[item_id]["quantity"]}')
                elif isinstance(bag[item_id], int):
                    bag[item_id] += quantity
                    messages.success(request, f'Updated {product.name} quantity to {bag[item_id]}')
                else:
                    bag[item_id] = {'quantity': quantity}
                    messages.success(request, f'Added {product.name} to your bag')
            else:
                bag[item_id] = {'quantity': quantity}
                messages.success(request, f'Added {product.name} to your bag')
        
        request.session['bag'] = bag
        return redirect(redirect_url)
    except Exception as e:
        logger.error("Error in add_to_bag: %s", traceback.format_exc())
        messages.error(request, 'An unexpected error occurred.')
        return redirect(reverse("home"))

def adjust_bag(request, item_id):
    product = get_object_or_404(Product, pk=item_id)
    item_id = str(item_id)
    quantity = int(request.POST.get('quantity'))
    size = request.POST.get('product_size', None)
    bag = request.session.get('bag', {})
    if size:
        if quantity > 0:
            bag[item_id]['items_by_size'][size] = quantity
            messages.success(request, f'Updated size {size.upper()} {product.name} quantity to {bag[item_id]["items_by_size"][size]}')
        else:
            del bag[item_id]['items_by_size'][size]
            if not bag[item_id]['items_by_size']:
                bag.pop(item_id)
            messages.success(request, f'Removed size {size.upper()} {product.name} from your bag')
    else:
        if quantity > 0:
            if isinstance(bag[item_id], dict) and 'quantity' in bag[item_id]:
                bag[item_id]['quantity'] = quantity
            else:
                bag[item_id] = {'quantity': quantity}
            messages.success(request, f'Updated {product.name} quantity to {bag[item_id]["quantity"]}')
        else:
            bag.pop(item_id)
            messages.success(request, f'Removed {product.name} from your bag')
    request.session['bag'] = bag
    return redirect(reverse('bag:view_bag'))

def remove_from_bag(request, item_id):
    try:
        product = get_object_or_404(Product, pk=item_id)
        item_id = str(item_id)
        size = request.POST.get('product_size', None)
        bag = request.session.get('bag', {})
        if size:
            del bag[item_id]['items_by_size'][size]
            if not bag[item_id]['items_by_size']:
                bag.pop(item_id)
            messages.success(request, f'Removed size {size.upper()} {product.name} from your bag')
        else:
            bag.pop(item_id)
            messages.success(request, f'Removed {product.name} from your bag')
        request.session['bag'] = bag
        return HttpResponse(status=200)
    except Exception as e:
        messages.error(request, f'Error removing item: {e}')
        return HttpResponse(status=500)
