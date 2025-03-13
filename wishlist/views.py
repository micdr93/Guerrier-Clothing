from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from products.models import Product
from .models import Wishlist, WishlistItem
from recommendations.utils import get_recommended_items


@login_required
def wishlist_home(request):
    wishlist = Wishlist.objects.filter(user=request.user).first()
    recommended_items = (
        get_recommended_items([item.product for item in wishlist.items.all()])
        if wishlist
        else []
    )

    # Get the IDs of products in the wishlist to pass to template
    wishlist_item_ids = (
        list(wishlist.items.values_list("product_id", flat=True))
        if wishlist
        else []
    )

    return render(
        request,
        "wishlist/wishlist_home.html",
        {
            "wishlist": wishlist,
            "recommended_items": recommended_items,
            "wishlist_item_ids": wishlist_item_ids,
        },
    )


@login_required
def add_to_wishlist(request, product_id):
    try:
        is_ajax = (
            request.method == "POST"
            or request.headers.get("X-Requested-With") == "XMLHttpRequest"
        )
        if is_ajax:
            product = get_object_or_404(Product, pk=product_id)
            
            # Get the first wishlist or create one if none exists
            wishlist = Wishlist.objects.filter(user=request.user).first()
            if not wishlist:
                wishlist = Wishlist.objects.create(user=request.user)
            
            # Check if the item already exists before creating it
            wishlist_item, item_created = WishlistItem.objects.get_or_create(
                wishlist=wishlist, product=product
            )
            
            return JsonResponse({
                "success": True,
                "in_wishlist": True,
                "message": f"{product.name} added to your wishlist."
            })
        return JsonResponse(
            {"success": False, "message": "Invalid request."},
            status=400
        )
    except Exception as e:
        # Log the error
        print(f"Error adding to wishlist: {str(e)}")
        return JsonResponse(
            {
                "success": False,
                "message": f"Error adding to wishlist: {str(e)}"
            },
            status=500
        )


@login_required
def remove_from_wishlist(request, product_id):
    try:
        is_ajax = (
            request.method == "POST"
            or request.headers.get("X-Requested-With") == "XMLHttpRequest"
        )
        if is_ajax:
            product = get_object_or_404(Product, pk=product_id)
            wishlist = Wishlist.objects.filter(user=request.user).first()

            if wishlist:
                wishlist_item = WishlistItem.objects.filter(
                    wishlist=wishlist, product=product
                ).first()
                if wishlist_item:
                    wishlist_item.delete()
                    return JsonResponse({
                        "success": True,
                        "in_wishlist": False,
                        "message": f"{product.name} removed from wishlist."
                    })

            return JsonResponse({
                "success": True,
                "in_wishlist": False,
                "message": "Item not found in wishlist."
            })

        return JsonResponse(
            {"success": False, "message": "Invalid request."},
            status=400
        )
    except Exception as e:
        # Log the error
        print(f"Error removing from wishlist: {str(e)}")
        return JsonResponse(
            {
                "success": False,
                "message": f"Error removing from wishlist: {str(e)}"
            },
            status=500
        )