from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.contrib import messages
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Avg, Min, Max
from django.views.generic import DeleteView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .forms import ProductForm, ReviewsForm
from .models import Product, Category, Size
from reviews.models import Review
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
    
    # Get all available sizes and colors
    sizes = Size.objects.all()
    colors = Product.objects.exclude(color=None).values_list('color', flat=True).distinct()
    
    # Initialize filter variables
    query_category = request.GET.get('category', category)
    query = request.GET.get('q', '').strip()
    price_min = request.GET.get('price_min')
    price_max = request.GET.get('price_max')
    selected_sizes = request.GET.getlist('size')
    selected_colors = request.GET.getlist('color')
    selected_genders = request.GET.getlist('gender')
    only_in_stock = request.GET.get('in_stock') == 'on'
    only_on_sale = request.GET.get('on_sale') == 'on'
    only_new = request.GET.get('is_new') == 'on'
    only_featured = request.GET.get('featured') == 'on'
    
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
    
    # Size filtering
    if selected_sizes:
        filter_applied = True
        products = products.filter(sizes__name__in=selected_sizes).distinct()
    
    # Color filtering
    if selected_colors:
        filter_applied = True
        products = products.filter(color__in=selected_colors)
    
    # Gender filtering
    if selected_genders:
        filter_applied = True
        products = products.filter(gender__in=selected_genders)
    
    # Stock filtering
    if only_in_stock:
        filter_applied = True
        products = products.filter(in_stock=True)
    
    # Sale filtering
    if only_on_sale:
        filter_applied = True
        products = products.filter(on_sale=True)
    
    # New products filtering
    if only_new:
        filter_applied = True
        products = products.filter(is_new=True)
    
    # Featured products filtering
    if only_featured:
        filter_applied = True
        products = products.filter(featured=True)

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
        'sizes': sizes,
        'colors': colors,
        'min_price': min_price,
        'max_price': max_price,
        'current_price_min': price_min or min_price,
        'current_price_max': price_max or max_price,
        'selected_sizes': selected_sizes,
        'selected_colors': selected_colors,
        'selected_genders': selected_genders,
        'only_in_stock': only_in_stock,
        'only_on_sale': only_on_sale,
        'only_new': only_new,
        'only_featured': only_featured,
        'filter_applied': filter_applied,
    }
    return render(request, 'products/products.html', context)

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
    form_class = ReviewsForm
    template_name = "products/edit_review.html"

    def form_valid(self, form):
        form.save()
        messages.success(self.request, "Your review has been updated!")
        return redirect(reverse_lazy("products:product_detail", kwargs={"product_id": self.object.product_id}))

def product_detail(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
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
def add_review(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    
    if Review.objects.filter(product=product, user=request.user).exists():
        messages.error(request, "You have already reviewed this product.")
        return redirect(reverse("products:product_detail", args=[product.id]))

    if request.method == "POST":
        review_form = ReviewsForm(request.POST)
        if review_form.is_valid():
            review = review_form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()

            messages.success(request, "Your review has been successfully added!")
            return redirect(reverse("products:product_detail", args=[product.id]))
        else:
            messages.error(request, "There was an error with your review submission. Please try again.")
    
    return redirect(reverse("products:product_detail", args=[product.id]))

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