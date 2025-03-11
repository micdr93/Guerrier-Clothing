from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.contrib import messages
from django.db.models import Min, Max, Q, Avg
from django.contrib.auth.decorators import login_required
from django.views.generic import DeleteView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
import random
from .forms import ProductForm
from products.models import Product, Category
from wishlist.models import Wishlist
from reviews.models import Review
from reviews.forms import ReviewForm


def calculate_average_rating(product):
    reviews = Review.objects.filter(product=product)
    if reviews.exists():
        return reviews.aggregate(Avg("rating"))["rating__avg"]
    return 0


def all_products(request, category=None):
    query_category = request.GET.get("category", category)
    if query_category:
        query_category_normalized = (
            query_category.lower().replace("-", " ").replace("_", " ").strip()
        )
        category_redirects = {
            "hats": "home:hats_view",
            "shirts": "home:shirts_view",
            "mugs": "home:mugs_view",
            "coasters": "home:coasters_view",
            "skateboard decks": "home:skateboard_decks_view",
            "skateboard_decks": "home:skateboard_decks_view",
        }
        if query_category_normalized in category_redirects:
            url = reverse(category_redirects[query_category_normalized])
            qs = request.GET.copy()
            qs.pop("category", None)
            if qs:
                url = f"{url}?{qs.urlencode()}"
            return redirect(url)
        try:
            category_obj = Category.objects.get(name__iexact=query_category)
            products = Product.active_products().filter(category=category_obj)
        except Category.DoesNotExist:
            products = Product.active_products().filter(
                category__name__icontains=query_category
            )
    else:
        products = Product.active_products()
    categories = Category.objects.all()
    price_range = products.aggregate(Min("price"), Max("price"))
    query = request.GET.get("q", "").strip()
    price_min = request.GET.get("price_min")
    price_max = request.GET.get("price_max")
    filter_applied = False
    active_category = None
    if query:
        filter_applied = True
        products = products.filter(
            Q(name__icontains=query)
            | Q(description__icontains=query)
            | Q(category__name__icontains=query)
        ).distinct()
    elif request.GET.get("homeware_filter") == "true":
        filter_applied = True
        products = products.filter(
            category__name__in=["mugs", "coasters", "skateboard_decks"]
        )
        active_category = "Homeware"
    elif request.GET.get("clothing_filter") == "true":
        filter_applied = True
        products = products.filter(category__name__in=["shirts", "hats"])
        active_category = "Clothing"
    elif query_category:
        filter_applied = True
        try:
            category_obj = Category.objects.get(name__iexact=query_category)
            products = products.filter(category=category_obj)
            active_category = category_obj.friendly_name or category_obj.name
        except Category.DoesNotExist:
            products = products.filter(category__name__icontains=query_category)
            active_category = query_category
    if price_min:
        filter_applied = True
        products = products.filter(price__gte=float(price_min))
    if price_max:
        filter_applied = True
        products = products.filter(price__lte=float(price_max))
    sort_param = request.GET.get("sort", "")
    if sort_param:
        parts = sort_param.split("_")
        sort_field = parts[0]
        direction = parts[1] if len(parts) > 1 else "asc"
        if sort_field == "price":
            products = products.order_by(f"{'' if direction == 'asc' else '-'}price")
        elif sort_field == "name":
            products = products.order_by(f"{'' if direction == 'asc' else '-'}name")
        elif sort_field == "category":
            products = products.order_by(
                f"{'' if direction == 'asc' else '-'}category__name"
            )
        elif sort_field == "rating":
            products = products.order_by(f"{'' if direction == 'asc' else '-'}rating")
    else:
        products = products.order_by("-featured", "-created_at")
    wishlist = None
    if request.user.is_authenticated:
        wishlist = Wishlist.objects.filter(user=request.user).first()
    context = {
        "products": products,
        "search_term": query,
        "current_categories": active_category,
        "categories": categories,
        "wishlist": wishlist,
        "current_sorting": sort_param if sort_param else "None_None",
        "min_price": price_range["price__min"] or 0,
        "max_price": price_range["price__max"] or 0,
        "current_price_min": price_min or (price_range["price__min"] or 0),
        "current_price_max": price_max or (price_range["price__max"] or 0),
        "filter_applied": filter_applied,
    }
    return render(request, "products/products.html", context)


def product_detail(request, product_id):
    product = get_object_or_404(
        Product.objects.select_related("category"), pk=product_id
    )
    if "review_added" in request.GET or "review_deleted" in request.GET:
        product.update_rating()
        product.refresh_from_db()
    reviews = Review.objects.filter(product=product).order_by("-created_on")
    related_products = list(
        Product.objects.filter(category=product.category).exclude(pk=product_id)
    )
    if len(related_products) >= 4:
        related_products = random.sample(related_products, 4)

    is_in_wishlist = False
    if request.user.is_authenticated:
        is_in_wishlist = Wishlist.objects.filter(
            user=request.user, items__product=product
        ).exists()

    context = {
        "product": product,
        "reviews": reviews,
        "related_products": related_products,
        "is_in_wishlist": is_in_wishlist,
    }
    return render(request, "products/product_detail.html", context)