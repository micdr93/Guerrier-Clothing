from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from products.models import Product
from .models import Wishlist, WishlistItem

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
    wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
    
    # Create or get the WishlistItem linking this product to the wishlist
    wishlist_item, item_created = WishlistItem.objects.get_or_create(
        wishlist=wishlist,
        product=product
    )
    
    if item_created:
        messages.success(request, f'{product.name} added to your wishlist.')
    else:
        messages.info(request, f'{product.name} is already in your wishlist.')
    
    return redirect(request.META.get('HTTP_REFERER', 'products'))


@login_required
def remove_from_wishlist(request, product_id):
    """Remove a product from the wishlist"""
    product = get_object_or_404(Product, pk=product_id)
    wishlist = Wishlist.objects.filter(user=request.user).first()
    
    if wishlist:
        # Delete the WishlistItem for this product if it exists
        wishlist_item = WishlistItem.objects.filter(wishlist=wishlist, product=product).first()
        if wishlist_item:
            wishlist_item.delete()
            messages.success(request, f'{product.name} removed from your wishlist.')
        else:
            messages.info(request, f'{product.name} was not in your wishlist.')
    
    return redirect(request.META.get('HTTP_REFERER', 'products'))
