from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.contrib import messages
from django.contrib.auth import logout
from django.db.models import Min, Max, Q, Avg
from django.contrib.auth.decorators import login_required
from django.views.generic import DeleteView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
import random
from .forms import ContactForm, NewsletterForm, ProductForm
from .models import NewsletterSubscription
from products.models import Product, Category
from wishlist.models import Wishlist
from reviews.models import Review
from reviews.forms import ReviewForm

def index(request):
    newsletter_form = NewsletterForm()
    if request.method == 'POST' and 'email' in request.POST:
        email = request.POST.get('email')
        newsletter_form = NewsletterForm({'email': email})
        if newsletter_form.is_valid():
            try:
                newsletter_form.save()
                messages.success(request, "Thank you for subscribing to our newsletter!")
            except:
                messages.error(request, "You're already subscribed to our newsletter.")
    context = {'banner_image': '/media/banners/banner.png', 'newsletter_form': newsletter_form}
    return render(request, 'home/index.html', context)

def instant_logout(request):
    logout(request)
    messages.success(request, "You have been successfully logged out.")
    return redirect('index')

def shirts_view(request):
    products = Product.objects.filter(category__name__iexact='shirts')
    context = {'products': products, 'current_category': 'shirts'}
    return render(request, 'home/shirts.html', context)

def hats_view(request):
    products = Product.objects.filter(category__id=2)
    wishlist_item_ids = set()
    wishlist = None
    if request.user.is_authenticated:
        wishlist = Wishlist.objects.filter(user=request.user).first()
        if wishlist:
            wishlist_item_ids = set(wishlist.items.values_list("product_id", flat=True))
    context = {'products': products, 'wishlist': wishlist, 'wishlist_item_ids': wishlist_item_ids}
    return render(request, 'home/hats.html', context)

def products_view(request):
    products = Product.objects.filter(is_active=True)
    categories = Category.objects.all()
    context = {
        'products': products,
        'categories': categories,
        'current_sorting': 'None_None',
        'min_price': products.aggregate(Min('price'))['price__min'],
        'max_price': products.aggregate(Max('price'))['price__max'],
        'current_price_min': products.aggregate(Min('price'))['price__min'],
        'current_price_max': products.aggregate(Max('price'))['price__max'],
        'filter_applied': False,
    }
    return render(request, 'products/products.html', context)

def privacy_policy(request):
    return render(request, 'home/privacy_policy.html')

def returns(request):
    return render(request, 'home/returns.html')

def contact(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Thank you, your email has been sent. We will contact you shortly.")
            return redirect("contact")
        else:
            messages.error(request, "Form submission failed. Please check the form and try again.")
    else:
        form = ContactForm()
    return render(request, "home/contact.html", {"form": form})

def all_products(request, category=None):
    query_category = request.GET.get('category', category)
    if query_category:
        query_category_normalized = str(query_category).lower().replace('-', ' ').replace('_', ' ').strip()
        category_redirects = {
            'hats': 'hats_view',
            'shirts': 'shirts_view',
            'mugs': 'mugs_view', 
            'coasters': 'coasters_view',
            'skateboard decks': 'skateboard_decks_view',
        }
        if query_category_normalized in category_redirects:
            return redirect(category_redirects[query_category_normalized])
        try:
            category_obj = Category.objects.get(name__iexact=query_category)
            db_category_name = category_obj.name.lower().replace('-', ' ').replace('_', ' ')
            if db_category_name in category_redirects:
                return redirect(category_redirects[db_category_name])
        except Category.DoesNotExist:
            pass
    products = Product.active_products()
    categories = Category.objects.all()
    price_range = products.aggregate(Min('price'), Max('price'))
    min_price = price_range['price__min']
    max_price = price_range['price__max']
    query = request.GET.get('q', '').strip()
    price_min = request.GET.get('price_min')
    price_max = request.GET.get('price_max')
    filter_applied = False
    active_category = None
    if query:
        filter_applied = True
        products = products.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(category__name__icontains=query)
        ).distinct()
    elif request.GET.get('homeware_filter') == 'true':
        filter_applied = True
        products = products.filter(category__name__in=['mugs', 'coasters', 'skateboard_decks'])
        active_category = 'Homeware'
    elif request.GET.get('clothing_filter') == 'true':
        filter_applied = True
        products = products.filter(category__name__in=['shirts', 'Hats'])
        active_category = 'Clothing'
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
            products = products.order_by('rating' if direction == 'asc' else '-rating')
    else:
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
    return render(request, 'products/products.html', context)

def mugs_view(request):
    products = Product.objects.filter(category__id=3)
    return render(request, 'home/mugs.html', {'products': products})

def coasters_view(request):
    products = Product.objects.filter(category__id=4)
    return render(request, 'home/coasters.html', {'products': products})

def skateboard_decks_view(request):
    products = Product.objects.filter(category__id=5)
    return render(request, 'home/skateboard_decks.html', {'products': products})

class DeleteReview(LoginRequiredMixin, DeleteView):
    model = Review
    template_name = "products/delete_review.html"
    success_message = "Review deleted successfully."
    def test_func(self):
        review = self.get_object()
        return self.request.user == review.user or self.request.user.is_superuser
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
    product = get_object_or_404(Product.objects.select_related('category'), pk=product_id)
    if 'review_added' in request.GET or 'review_deleted' in request.GET:
        product.update_rating()
        product.refresh_from_db()
    reviews = Review.objects.filter(product=product).order_by("-created_on")
    related_products = list(Product.objects.filter(category=product.category).exclude(pk=product_id))
    if len(related_products) >= 4:
        related_products = random.sample(related_products, 4)
    context = {"product": product, "reviews": reviews, "related_products": related_products}
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
        messages.error(request, 'Failed to add product. Please ensure the form is valid.')
    else:
        form = ProductForm()
    return render(request, 'products/add_product.html', {'form': form})

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
        messages.error(request, 'Failed to update product. Please ensure the form is valid.')
    else:
        form = ProductForm(instance=product)
        messages.info(request, f'You are editing {product.name}')
    return render(request, 'products/edit_product.html', {'form': form, 'product': product})

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
    return render(request, 'products/search_results.html', {'products': products, 'search_term': query})
