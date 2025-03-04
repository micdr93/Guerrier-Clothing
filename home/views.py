from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import logout
from .forms import ContactForm
from products.models import Product
from wishlist.models import Wishlist
from .forms import NewsletterForm
from .models import NewsletterSubscription

def index(request):

    if request.method == 'POST':
        newsletter_form = NewsletterForm(request.POST)
        if newsletter_form.is_valid():
            try:
                newsletter_form.save()
                messages.success(request, "Thank you for subscribing to our newsletter!")
            except:
                messages.error(request, "You're already subscribed to our newsletter.")
    else:
        newsletter_form = NewsletterForm()
        
    context = {
        'banner_image': '/media/banners/banner.png',
        'newsletter_form': newsletter_form
    }
    return render(request, 'home/index.html', context)

def instant_logout(request):
    logout(request)
    messages.success(request, "You have been successfully logged out.")
    return redirect('home')

def shirts_view(request):
    products = Product.objects.filter(category__name__iexact='shirts')
    context = {
        'products': products,
        'current_category': 'shirts',
    }
    return render(request, 'home/shirts.html', context)

def hats_view(request):
    products = Product.objects.filter(category__id=2)
    wishlist_item_ids = set()
    wishlist = None
    if request.user.is_authenticated:
        wishlist = Wishlist.objects.filter(user=request.user).first()
        if wishlist:
            wishlist_item_ids = set(wishlist.items.values_list("product_id", flat=True))
    context = {
        'products': products,
        'wishlist': wishlist,
        'wishlist_item_ids': wishlist_item_ids,
    }
    return render(request, 'home/hats.html', context)

def products_view(request):
    products = Product.objects.filter(is_active=True)
    wishlist_item_ids = set()
    wishlist = None
    if request.user.is_authenticated:
        wishlist = Wishlist.objects.filter(user=request.user).first()
        if wishlist:
            wishlist_item_ids = set(wishlist.items.values_list("product_id", flat=True))
    context = {
        'products': products,
        'wishlist': wishlist,
        'wishlist_item_ids': wishlist_item_ids,
    }
    return render(request, 'home/products.html', context)

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
    context = {
        "form": form,
    }
    return render(request, "home/contact.html", context)

def all_products(request):
    return render(request, 'products.html', {})

# Homeware views using long-term fix with proper category assignments
def mugs_view(request):
    
    products = Product.objects.filter(category__id=3)
    return render(request, 'home/mugs.html', {'products': products})

def coasters_view(request):
    
    products = Product.objects.filter(category__id=4)
    return render(request, 'home/coasters.html', {'products': products})

def skateboard_decks_view(request):

    products = Product.objects.filter(category__id=5)
    return render(request, 'home/skateboard_decks.html', {'products': products})
