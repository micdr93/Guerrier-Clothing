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
    recommended_items = get_recommended_items([item.product for item in wishlist.items.all()]) if wishlist else []
    return render(request, "wishlist/wishlist_home.html", {"wishlist": wishlist, "recommended_items": recommended_items})


@login_required
def add_to_wishlist(request, product_id):
    if request.method == "POST":
        product = get_object_or_404(Product, pk=product_id)
        wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
        wishlist_item, item_created = WishlistItem.objects.get_or_create(wishlist=wishlist, product=product)
        return JsonResponse({"success": True, "in_wishlist": True, "message": f"{product.name} added to your wishlist."})
    return JsonResponse({"success": False, "message": "Invalid request."}, status=400)


@login_required
def remove_from_wishlist(request, product_id):
    if request.method == "POST":
        product = get_object_or_404(Product, pk=product_id)
        wishlist = Wishlist.objects.filter(user=request.user).first()
        if wishlist:
            wishlist_item = WishlistItem.objects.filter(wishlist=wishlist, product=product).first()
            if wishlist_item:
                wishlist_item.delete()
                return JsonResponse({"success": True, "in_wishlist": False, "message": f"{product.name} removed from wishlist."})
        return JsonResponse({"success": True, "in_wishlist": False, "message": "Item not found in wishlist."})
    return JsonResponse({"success": False, "message": "Invalid request."}, status=400)
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
    recommended_items = get_recommended_items([item.product for item in wishlist.items.all()]) if wishlist else []
    
    # Get the IDs of products in the wishlist to pass to template
    wishlist_item_ids = list(wishlist.items.values_list('product_id', flat=True)) if wishlist else []
    
    return render(request, "wishlist/wishlist_home.html", {
        "wishlist": wishlist, 
        "recommended_items": recommended_items,
        "wishlist_item_ids": wishlist_item_ids
    })


@login_required
def add_to_wishlist(request, product_id):
    if request.method == "POST" or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        product = get_object_or_404(Product, pk=product_id)
        wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
        
        wishlist_item, created = WishlistItem.objects.get_or_create(
            wishlist=wishlist, 
            product=product
        )
        
        return JsonResponse({
            "success": True, 
            "in_wishlist": True, 
            "message": f"{product.name} added to your wishlist."
        })
    
    return JsonResponse({"success": False, "message": "Invalid request."}, status=400)


@login_required
def remove_from_wishlist(request, product_id):
    if request.method == "POST" or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        product = get_object_or_404(Product, pk=product_id)
        wishlist = Wishlist.objects.filter(user=request.user).first()
        
        if wishlist:
            wishlist_item = WishlistItem.objects.filter(wishlist=wishlist, product=product).first()
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
    
    return JsonResponse({"success": False, "message": "Invalid request."}, status=400)