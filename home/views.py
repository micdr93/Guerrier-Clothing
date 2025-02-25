from django.shortcuts import render, redirect
from products.models import Product, Category
from .forms import ContactForm
from django.contrib import messages
from django.contrib.auth import logout

def index(request):

    return render(request, 'home/index.html',)




def instant_logout(request):
    """Log out the user immediately without confirmation screen"""
    logout(request)
    messages.success(request, "You have been successfully logged out.")
    return redirect('home')


def shirts_view(request):
    """A view to show all shirts"""
    # Filter products that are shirts
    products = Product.objects.filter(category__name='shirts')
    
    context = {
        'products': products,
        'current_category': 'shirts',
    }
    
    return render(request, 'home/shirts.html', context)


def products_view(request):
    """A view to show all products"""
    products = Product.objects.filter(is_active=True)
    
    context = {
        'products': products,
    }
    
    return render(request, 'home/products.html', context)

# View for rendering the privacy policy page
def privacy_policy(request):
    """
    FAQs Page
    """
    return render(request, "home/privacy_policy.html")


def hats_view(request):
 
    return render(request, 'home/hats.html', context={})

# View for rendering the returns page
def returns(request):

    return render(request, "home/returns.html")


# View for handling the contact form submission
def contact(request):
    """
    View to return Contact Us form
    """

    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                "Thank you, your email has been sent. We will contact you shortly.",
            )
            return redirect("contact")
        else:
            messages.error(
                request, "Form submission failed. Please check the form and try again."
            )
    else:
        form = ContactForm()

    context = {
        "form": form,
    }

    return render(request, "home/contact.html", context)


