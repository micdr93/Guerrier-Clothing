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
    return reviews.aggregate(Avg("rating"))["rating__avg"] if reviews.exists() else 0


def all_products(request, category=None):
    query_category = request.GET.get("category", category)
    if query_category:
        query_category_normalized = (
            query_category.lower().replace("-", " ").replace("_", " ").strip()
        )
        try:
            category_obj = Category.objects.get(name__iexact=query_category_normalized)
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
    price_min, price_max = request.GET.get("price_min"), request.GET.get("price_max")
    filter_applied = bool(query or price_min or price_max)

    if query:
        products = products.filter(
            Q(name__icontains=query)
            | Q(description__icontains=query)
            | Q(category__name__icontains=query)
        ).distinct()

    if price_min:
        products = products.filter(price__gte=float(price_min))
    if price_max:
        products = products.filter(price__lte=float(price_max))

    sort_param = request.GET.get("sort", "")
    if sort_param:
        parts = sort_param.split("_")
        sort_field, direction = parts[0], parts[1] if len(parts) > 1 else "asc"
        if sort_field in ["price", "name", "rating", "category"]:
            products = products.order_by(
                f"{'' if direction == 'asc' else '-'}{sort_field}"
            )
    else:
        products = products.order_by("-featured", "-created_at")

    wishlist = (
        Wishlist.objects.filter(user=request.user).first()
        if request.user.is_authenticated
        else None
    )

    context = {
        "products": products,
        "search_term": query,
        "current_categories": query_category,
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
    related_products = random.sample(related_products, min(len(related_products), 4))

    is_in_wishlist = (
        request.user.is_authenticated
        and Wishlist.objects.filter(user=request.user, items__product=product).exists()
    )

    context = {
        "product": product,
        "reviews": reviews,
        "related_products": related_products,
        "is_in_wishlist": is_in_wishlist,
    }
    return render(request, "products/product_detail.html", context)


@login_required
def add_product(request):
    if not request.user.is_superuser:
        messages.error(request, "Sorry, only store owners can do that.")
        return redirect(reverse("home"))

    form = ProductForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        product = form.save()
        messages.success(request, "Successfully added product!")
        return redirect(reverse("products:product_detail", args=[product.id]))

    messages.error(request, "Failed to add product. Please ensure the form is valid.")
    return render(request, "products/add_product.html", {"form": form})


@login_required
def edit_product(request, product_id):
    if not request.user.is_superuser:
        messages.error(request, "Sorry, only store owners can do that.")
        return redirect(reverse("home"))

    product = get_object_or_404(Product, pk=product_id)
    form = ProductForm(request.POST or None, request.FILES or None, instance=product)

    if form.is_valid():
        form.save()
        messages.success(request, "Successfully updated product!")
        return redirect(reverse("products:product_detail", args=[product.id]))

    messages.info(request, f"You are editing {product.name}")
    return render(
        request, "products/edit_product.html", {"form": form, "product": product}
    )


@login_required
def delete_product(request, product_id):
    if not request.user.is_superuser:
        messages.error(request, "Sorry, only store owners can do that.")
        return redirect(reverse("home"))

    product = get_object_or_404(Product, pk=product_id)
    product.delete()
    messages.success(request, "Product deleted!")
    return redirect(reverse("products:products"))


def search_results(request):
    query = request.GET.get("q", "").strip()
    products = Product.objects.filter(
        Q(name__icontains=query)
        | Q(description__icontains=query)
        | Q(category__name__icontains=query)
    ).distinct()
    return render(
        request,
        "products/search_results.html",
        {"products": products, "search_term": query},
    )


class DeleteReview(LoginRequiredMixin, DeleteView):
    model = Review
    template_name = "products/delete_review.html"
    success_message = "Review deleted successfully."

    def test_func(self):
        review = self.get_object()
        return self.request.user == review.user or self.request.user.is_superuser

    def get_success_url(self):
        return reverse(
            "products:product_detail", kwargs={"product_id": self.object.product_id}
        )


class UpdateReview(LoginRequiredMixin, UpdateView):
    model = Review
    form_class = ReviewForm
    template_name = "products/edit_review.html"

    def form_valid(self, form):
        form.save()
        messages.success(self.request, "Your review has been updated!")
        return redirect(
            reverse(
                "products:product_detail", kwargs={"product_id": self.object.product_id}
            )
        )


# ✅ Category Views for Individual Product Categories


def mugs_view(request):
    products = Product.objects.filter(category__name__iexact="mugs")
    return render(request, "products/mugs.html", {"products": products})


def coasters_view(request):
    products = Product.objects.filter(category__name__iexact="coasters")
    return render(request, "products/coasters.html", {"products": products})


def skateboard_decks_view(request):
    products = Product.objects.filter(category__name__iexact="skateboard decks")
    return render(request, "products/skateboard_decks.html", {"products": products})


def shirts_view(request):
    products = Product.objects.filter(category__name__iexact="shirts")
    return render(request, "products/shirts.html", {"products": products})


def hats_view(request):
    products = Product.objects.filter(category__name__iexact="hats")
    return render(request, "products/hats.html", {"products": products})
