from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from products.models import Product

def view_bag(request):
    bag = request.session.get('bag', {})
    context = {'bag': bag}
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
