from django.shortcuts import render, redirect, get_object_or_404
from products.models import Product
from django.contrib import messages

def index(request):
    # Retrieve bag items from session (if any) to display on the bag homepage.
    bag = request.session.get('bag', {})
    context = {'bag': bag}
    return render(request, 'bag/bag_home.html', context)

def add_to_bag(request, product_id):
    # Retrieve the product using the provided product_id.
    product = get_object_or_404(Product, pk=product_id)
    
    # Get the current bag from the session or initialize an empty bag.
    bag = request.session.get('bag', {})

    # Use the product's id (as a string) as the key.
    product_key = str(product_id)
    if product_key in bag:
        bag[product_key] += 1  # Increment quantity if already in bag.
    else:
        bag[product_key] = 1   # Otherwise, add it with quantity 1.

    # Save the updated bag back into the session.
    request.session['bag'] = bag

    # Optionally, send a success message.
    messages.success(request, f'Added {product.name} to your bag.')

    # Redirect to the bag homepage.
    return redirect('bag_home')
