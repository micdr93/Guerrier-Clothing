from django.shortcuts import render, redirect
from products.models import Product, Category
from .forms import ContactForm
from django.contrib import messages


def index(request):

    return render(request, 'home/index.html',)



# View for rendering the privacy policy page
def privacy_policy(request):
    """
    FAQs Page
    """
    return render(request, "home/privacy_policy.html")


def shirts_view(request):
   
    return render(request, 'home/shirts.html', context={})


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

