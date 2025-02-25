from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib import messages
from django.views.generic import UpdateView, DeleteView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.db.models import Q
from django.db.models.functions import Lower
from .forms import ProductForm, ReviewsForm
from .widgets import CustomClearableFileInput
from .models import Product, Category
from reviews.models import Review
from profiles.models import UserProfile
from wishlist.models import Wishlist
import random

# renders all products from database
def all_products(request):
    products = Product.objects.all()
    user = request.user
    query = None
    categories = None
    sort = None
    direction = None

    if user.is_authenticated:
        wishlist, created = Wishlist.objects.get_or_create(user=user)
    else:
        wishlist = None

    if request.GET:
        if 'sort' in request.GET:
            sortkey = request.GET['sort']
            sort = sortkey
            if sortkey == 'name':
                sortkey = 'lower_name'
                products = products.annotate(lower_name=Lower('name'))
            elif sortkey == 'category':
                sortkey = 'category__name'
            if 'direction' in request.GET:
                direction = request.GET['direction']
                if direction == 'desc':
                    sortkey = f'-{sortkey}'
            products = products.order_by(sortkey)

        if 'gender' in request.GET:
            gender = request.GET['gender']
            if gender:
                products = products.filter(gender=gender)
        
        if 'category' in request.GET:
            categories = request.GET['category']
            if categories:
                categories = categories.split(',')
                products = products.filter(category__name__in=categories)
                categories = Category.objects.filter(name__in=categories)

        if 'q' in request.GET:
            query = request.GET['q']
            if not query:
                messages.error(request, "You didn't enter any search criteria!")
                return redirect(reverse('products'))

            queries = Q(name__icontains=query) | Q(description__icontains=query)
            products = products.filter(queries)

    current_sorting = f'{sort}_{direction}'

    context = {
        'products': products,
        'search_term': query,
        'current_categories': categories,
        'current_sorting': current_sorting,
        "wishlist": wishlist,
    }

    return render(request, 'products/products.html', context)

def all_products(request):
    products = Product.objects.all()
    wishlist = None
    if request.user.is_authenticated:
        wishlist = Wishlist.objects.filter(user=request.user).first()
    
    context = {
        'products': products,
        'wishlist': wishlist,
    }
    return render(request, 'products/products.html', context)

# view for product detail page
def product_detail(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    reviews = Review.objects.filter(product=product).order_by("-created_on")

    related_products = list(
        Product.objects.filter(category=product.category).exclude(pk=product_id)
    )
    if len(related_products) >= 4:
        related_products = random.sample(related_products, 4)

    if not request.user.is_authenticated:
        template = "products/product_detail.html"
        context = {
            "product": product,
            "reviews": reviews,
            "related_products": related_products,
        }
        return render(request, template, context)
    else:
        user = request.user
        wishlist = Wishlist.objects.filter(user=user, items__product__id=product_id).exists()

        template = "products/product_detail.html"
        context = {
            "product": product,
            "reviews": reviews,
            "related_products": related_products,
            "wishlist": wishlist,
        }
        return render(request, template, context)


# view fom admin adding a product
@login_required
def add_product(request):
    if not request.user.is_superuser:
        messages.error(request, 'Sorry, only store owners can do that.')
        return redirect(reverse('home'))

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            messages.success(request, 'Successfully added product!')
            return redirect(reverse('product_detail', args=[product.id]))
        else:
            messages.error(request, 'Failed to add product. Please ensure the form is valid.')
    else:
        form = ProductForm()

    template = 'products/add_product.html'
    context = {
        'form': form,
    }

    return render(request, template, context)


# view to edit a product
@login_required
def edit_product(request, product_id):
    if not request.user.is_superuser:
        messages.error(request, 'Sorry, only store owners can do that.')
        return redirect(reverse('home'))

    product = get_object_or_404(Product, pk=product_id)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Successfully updated product!')
            return redirect(reverse('product_detail', args=[product.id]))
        else:
            messages.error(request, 'Failed to update product. Please ensure the form is valid.')
    else:
        form = ProductForm(instance=product)
        messages.info(request, f'You are editing {product.name}')

    template = 'products/edit_product.html'
    context = {
        'form': form,
        'product': product,
    }

    return render(request, template, context)


# view to delete a product
@login_required
def delete_product(request, product_id):
    if not request.user.is_superuser:
        messages.error(request, 'Sorry, only store owners can do that.')
        return redirect(reverse('home'))

    product = get_object_or_404(Product, pk=product_id)
    product.delete()
    messages.success(request, 'Product deleted!')
    return redirect(reverse('products'))


# view to add a review
@login_required
def add_review(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    if request.method == "POST":
        review_form = ReviewsForm(request.POST)

        if review_form.is_valid():
            try:
                Review.objects.create(
                    product=product,
                    user=request.user,
                    title=request.POST["title"],
                    review=request.POST["review"],
                )
                reviews = Review.objects.filter(product=product)
                messages.success(request, "Your review has been successfully added!")
                return redirect(reverse("product_detail", args=[product.id]))
            except IntegrityError:
                messages.error(request, "You have already reviewed this product.")
                return redirect(reverse("product_detail", args=[product.id]))
        else:
            messages.error(request, "Your review has not been submitted.")
    return redirect(reverse("product_detail", args=[product.id]))


# view to update a review
class UpdateReview(
    LoginRequiredMixin, SuccessMessageMixin, UserPassesTestMixin, UpdateView
):

    model = Review
    form_class = ReviewsForm
    template_name = "products/edit_review.html"
    success_message = "Your review was updated!"

    def test_func(self):
        review = self.get_object()
        user = self.request.user
        return user == review.user or user.is_superuser

    def get_success_url(self):
        return reverse("product_detail", kwargs={"product_id": self.object.product_id})


# view to delete a review
class DeleteReview(LoginRequiredMixin, UserPassesTestMixin, DeleteView):

    model = Review
    template_name = "products/delete_review.html"
    success_message = "Review deleted successfully."

    def test_func(self):
        review = self.get_object()
        user = self.request.user
        return user == review.user or user.is_superuser

    def get_success_url(self):
        return reverse("product_detail", kwargs={"product_id": self.object.product_id})

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)
    
