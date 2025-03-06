from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from products.models import Product
from recommendations.utils import get_recommended_items

def bag_home(request):
    # Get the bag items stored in the session
    bag = request.session.get('bag', {})
    bag_product_ids = bag.keys() 
    user_products = Product.objects.filter(id__in=bag_product_ids)
    recommended_items = get_recommended_items(user_products)

    context = {
        'bag': bag,
        'recommended_items': recommended_items,
    }
    return render(request, 'bag/bag_home.html', context)

def view_bag(request):
    bag = request.session.get('bag', {})  
    cart_items = []
    cart_total = 0

    for product_id_str, quantity in bag.items():
        product_id = int(product_id_str)
        product = get_object_or_404(Product, pk=product_id)
        total_price = product.price * quantity  # Calculate the total price for this item
        cart_total += total_price

        cart_items.append({
            'product': product,
            'quantity': quantity,
            'total_price': total_price,
            'line_total': total_price,  # Add line_total here
        })

    context = {
        'cart': cart_items,       
        'cart_total': cart_total, 
    }
    return render(request, 'bag/bag_home.html', context)

def add_to_bag(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    bag = request.session.get('bag', {})
    product_key = str(product_id)

    # Add product to the bag or increment quantity if already added
    if product_key in bag:
        bag[product_key] += 1
    else:
        bag[product_key] = 1

    # Update the session with the new bag
    request.session['bag'] = bag
    messages.success(request, f'Added {product.name} to your bag.')

    return redirect('bag:view_bag')  # Redirect to view_bag

@csrf_exempt
def remove_from_bag(request, product_id):
    """Remove the item from the shopping bag"""
    
    try:
        product = get_object_or_404(Product, pk=product_id)
        bag = request.session.get('bag', {})
        
        product_key = str(product_id)
        if product_key in bag:
            del bag[product_key]
            messages.success(request, f'Removed {product.name} from your bag')
        
        request.session['bag'] = bag
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True})
        
        return redirect(reverse('bag:view_bag'))
    
    except Exception as e:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'error': str(e)}, status=500)
        
        messages.error(request, f'Error removing item: {e}')
        return redirect(reverse('bag:view_bag'))

@csrf_exempt
def update_bag(request, product_id):
    """Update the quantity of the specified product to the specified amount"""
    
    try:
        product = get_object_or_404(Product, pk=product_id)
        quantity = int(request.POST.get('quantity', 1))
        
        bag = request.session.get('bag', {})
        product_key = str(product_id)
        
        if quantity > 0:
            bag[product_key] = quantity
            messages.success(request, f'Updated {product.name} quantity to {quantity}')
        else:
            if product_key in bag:
                del bag[product_key]
                messages.success(request, f'Removed {product.name} from your bag')
        
        request.session['bag'] = bag
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True})
        
        return redirect(reverse('bag:view_bag'))
    except Exception as e:
        messages.error(request, f'Error updating bag: {e}')
        return redirect(reverse('bag:view_bag'))