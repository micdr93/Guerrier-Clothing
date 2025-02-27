from django.shortcuts import render, get_object_or_404
from products.models import Product

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
    return redirect('view_bag')

def remove_from_bag(request, product_id):
    bag = request.session.get('bag', {})
    product_key = str(product_id)
    if product_key in bag:
        del bag[product_key]
    request.session['bag'] = bag
    return redirect('view_bag')