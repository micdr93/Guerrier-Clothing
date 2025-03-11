from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from products.models import Product
from .models import Wishlist, WishlistItem
from recommendations.utils import get_recommended_items


@login_required
def wishlist_home(request):
    """
    Display the user's wishlist along with recommended items.
    """
    # Retrieve the user's wishlist (using the Wishlist model)
    wishlist = Wishlist.objects.filter(user=request.user).first()

    # If the wishlist exists, compute recommendations based on its items
    if wishlist:
        user_products = [item.product for item in wishlist.items.all()]
        recommended_items = get_recommended_items(user_products)
    else:
        recommended_items = []

    context = {
        "wishlist": wishlist,
        "recommended_items": recommended_items,
    }
    return render(request, "wishlist/wishlist_home.html", context)


@login_required
def add_to_wishlist(request, product_id):
    """
    Add a product to the user's wishlist.
    """
    product = get_object_or_404(Product, pk=product_id)
    wishlist, _ = Wishlist.objects.get_or_create(user=request.user)

    # Create or get the WishlistItem linking this product to the wishlist
    wishlist_item, item_created = WishlistItem.objects.get_or_create(
        wishlist=wishlist, product=product
    )

    if item_created:
        messages.success(request, f"{product.name} added to your wishlist.")
    else:
        messages.info(request, f"{product.name} is already in your wishlist.")

    return redirect(request.META.get("HTTP_REFERER", "products"))


@login_required
def remove_from_wishlist(request, product_id):
    """
    Remove a product from the user's wishlist.
    """
    product = get_object_or_404(Product, pk=product_id)
    wishlist = Wishlist.objects.filter(user=request.user).first()

    if wishlist:
        wishlist_item = WishlistItem.objects.filter(
            wishlist=wishlist, product=product
        ).first()
        if wishlist_item:
            wishlist_item.delete()
            messages.success(request, f"{product.name} removed from your wishlist.")
        else:
            messages.info(request, f"{product.name} was not in your wishlist.")

    return redirect(request.META.get("HTTP_REFERER", "products"))
