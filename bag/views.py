from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from django.shortcuts import redirect
from products.models import Product
from recommendations.utils import get_recommended_items


def bag_home(request):

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
        total_price = product.price * quantity
        cart_total += total_price

        cart_items.append({
            'product': product,
            'quantity': quantity,
            'total_price': total_price,
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
    if product_key in bag:
        bag[product_key] += 1
    else:
        bag[product_key] = 1
    request.session['bag'] = bag
    messages.success(request, f'Added {product.name} to your bag.')
    return redirect('bag:view_bag')

def remove_from_bag(request, product_id):
    bag = request.session.get('bag', {})
    product_key = str(product_id)
    if product_key in bag:
        del bag[product_key]
    return redirect('bag:view_bag')
