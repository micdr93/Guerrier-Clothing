from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.contrib import messages
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Avg, Min, Max
from django.views.generic import DeleteView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .forms import ProductForm
from .models import Product, Category, Size
from reviews.models import Review
from reviews.forms import ReviewForm
from wishlist.models import Wishlist
import random

def calculate_average_rating(product):
    reviews = Review.objects.filter(product=product)
    if reviews.exists():
        return reviews.aggregate(Avg('rating'))['rating__avg']
    return 0
def all_products(request, category=None):
    products = Product.active_products()
    categories = Category.objects.all()
    
    # Get min and max prices for range filters
    price_range = products.aggregate(Min('price'), Max('price'))
    min_price = price_range['price__min']
    max_price = price_range['price__max']
    
    # Initialize filter variables
    query_category = request.GET.get('category', category)
    query = request.GET.get('q', '').strip()
    price_min = request.GET.get('price_min')
    price_max = request.GET.get('price_max')
    
    filter_applied = False
    active_category = None
    
    # Handle search query
    if query:
        filter_applied = True
        products = products.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(category__name__icontains=query)
        ).distinct()
    
    # Handle category filtering
    elif request.GET.get('homeware_filter') == 'true':
        filter_applied = True
        homeware_categories = ['mugs', 'coasters', 'skateboard_decks']
        products = products.filter(category__name__in=homeware_categories)
        active_category = 'Homeware'
        
    elif request.GET.get('clothing_filter') == 'true':
        filter_applied = True
        clothing_categories = ['shirts', 'Hats']
        products = products.filter(category__name__in=clothing_categories)
        active_category = 'Clothing'
        
    elif query_category:
        filter_applied = True
        products = products.filter(category__name__iexact=query_category)
        active_category = query_category
    
    # Price filtering
    if price_min:
        filter_applied = True
        products = products.filter(price__gte=float(price_min))
    
    if price_max:
        filter_applied = True
        products = products.filter(price__lte=float(price_max))

    # Handle sorting
    sort = request.GET.get('sort')
    direction = request.GET.get('direction', 'asc')
    
    if sort:
        if sort == 'price':
            products = products.order_by(f"{'' if direction == 'asc' else '-'}price")
        elif sort == 'name':
            products = products.order_by(f"{'' if direction == 'asc' else '-'}name")
        elif sort == 'category':
            products = products.order_by(f"{'' if direction == 'asc' else '-'}category__name")
        elif sort == 'rating':
            # Handle None values for rating
            if direction == 'asc':
                products = products.order_by('rating')
            else:
                products = products.order_by('-rating')
    else:
        # Default sorting (featured products first, then newest)
        products = products.order_by('-featured', '-created_at')

    wishlist = None
    if request.user.is_authenticated:
        wishlist = Wishlist.objects.filter(user=request.user).first()

    context = {
        'products': products,
        'search_term': query,
        'current_categories': active_category,
        'categories': categories,
        'wishlist': wishlist,
        'current_sorting': f'{sort}_{direction}' if sort and direction else 'None_None',
        'min_price': min_price,
        'max_price': max_price,
        'current_price_min': price_min or min_price,
        'current_price_max': price_max or max_price,
        'filter_applied': filter_applied,
    }
    
    # Add cache control headers to prevent caching issues
    response = render(request, 'products/products.html', context)
    response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response

class DeleteReview(LoginRequiredMixin, DeleteView):
    model = Review
    template_name = "products/delete_review.html"
    success_message = "Review deleted successfully."

    def test_func(self):
        review = self.get_object()
        user = self.request.user
        return user == review.user or user.is_superuser

    def get_success_url(self):
        return reverse_lazy("products:product_detail", kwargs={"product_id": self.object.product_id})

class UpdateReview(LoginRequiredMixin, UpdateView):
    model = Review
    form_class = ReviewForm
    template_name = "products/edit_review.html"

    def form_valid(self, form):
        form.save()
        messages.success(self.request, "Your review has been updated!")
        return redirect(reverse_lazy("products:product_detail", kwargs={"product_id": self.object.product_id}))

def product_detail(request, product_id):
    # Always get a fresh product instance from the database
    product = get_object_or_404(Product.objects.select_related('category'), pk=product_id)
    
    # Check if a review was just added
    if 'review_added' in request.GET or 'review_deleted' in request.GET:
        # Force a recalculation of the rating to ensure it's up to date
        product.update_rating()
        # Refresh the product instance to get the latest data
        product.refresh_from_db()
        
    reviews = Review.objects.filter(product=product).order_by("-created_on")
    related_products = list(Product.objects.filter(category=product.category).exclude(pk=product_id))
    if len(related_products) >= 4:
        related_products = random.sample(related_products, 4)
    
    context = {
        "product": product,
        "reviews": reviews,
        "related_products": related_products,
    }
    
    if request.user.is_authenticated:
        context["wishlist"] = Wishlist.objects.filter(user=request.user, items__product__id=product_id).exists()
    
    return render(request, "products/product_detail.html", context)

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
            return redirect(reverse('products:product_detail', args=[product.id]))
        else:
            messages.error(request, 'Failed to add product. Please ensure the form is valid.')
    else:
        form = ProductForm()
    template = 'products/add_product.html'
    context = {'form': form}
    return render(request, template, context)

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
            return redirect(reverse('products:product_detail', args=[product.id]))
        else:
            messages.error(request, 'Failed to update product. Please ensure the form is valid.')
    else:
        form = ProductForm(instance=product)
        messages.info(request, f'You are editing {product.name}')
    template = 'products/edit_product.html'
    context = {'form': form, 'product': product}
    return render(request, template, context)

@login_required
def delete_product(request, product_id):
    if not request.user.is_superuser:
        messages.error(request, 'Sorry, only store owners can do that.')
        return redirect(reverse('home'))
    product = get_object_or_404(Product, pk=product_id)
    product.delete()
    messages.success(request, 'Product deleted!')
    return redirect(reverse('products:products'))

def search_results(request):
    query = request.GET.get('q', '').strip()
    products = Product.objects.filter(
        Q(name__icontains=query) | 
        Q(description__icontains=query) | 
        Q(category__name__icontains=query)
    ).distinct()
    context = {'products': products, 'search_term': query}
    return render(request, 'products/search_results.html', context)