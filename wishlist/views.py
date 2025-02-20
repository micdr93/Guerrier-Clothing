from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from products.models import Product
from .models import Wishlist

@login_required
def wishlist_home(request):
    """Display the user's wishlist"""
    wishlist = Wishlist.objects.filter(user=request.user).first()
    context = {
        'wishlist': wishlist
    }
    return render(request, 'wishlist/wishlist_home.html', context)

@login_required
def add_to_wishlist(request, product_id):
    """Add a product to the wishlist"""
    product = get_object_or_404(Product, pk=product_id)
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    wishlist.products.add(product)
    messages.success(request, f'{product.name} added to your wishlist')
    return redirect(request.META.get('HTTP_REFERER', 'products'))

@login_required
def remove_from_wishlist(request, product_id):
    """Remove a product from the wishlist"""
    product = get_object_or_404(Product, pk=product_id)
    wishlist = Wishlist.objects.filter(user=request.user).first()
    if wishlist:
        wishlist.products.remove(product)
        messages.success(request, f'{product.name} removed from your wishlist')
    return redirect(request.META.get('HTTP_REFERER', 'products'))