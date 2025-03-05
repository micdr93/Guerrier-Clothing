from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
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

def remove_from_bag(request, product_id):
    bag = request.session.get('bag', {})
    product_key = str(product_id)

    # Check if the item exists in the bag
    if product_key in bag:
        del bag[product_key]  # Remove the item from the bag
        request.session['bag'] = bag  # Update the session with the modified bag

    return redirect('bag:view_bag')  # Redirect back to the bag view

def update_bag(request, product_id):
    bag = request.session.get('bag', {})
    product_key = str(product_id)

    # Check if the product is in the bag and update the quantity
    if product_key in bag:
        quantity = request.POST.get('quantity', 1)  # Get the updated quantity from the form
        try:
            quantity = int(quantity)  # Ensure it's an integer
            if quantity > 0:
                bag[product_key] = quantity  # Update the quantity in the bag
            else:
                del bag[product_key]  # If quantity is 0 or less, remove the item
        except ValueError:
            pass  # Handle invalid quantity values gracefully

    # Save the updated session and redirect to the cart view
    request.session['bag'] = bag
    return redirect('bag:view_bag')  # Redirect back to the cart