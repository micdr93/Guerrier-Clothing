from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib import messages
from django.conf import settings
from django.views.decorators.http import require_POST
from django.http import HttpResponse
from .forms import OrderForm
from .models import Order, OrderLineItem
from products.models import Product
from bag.contexts import bag_contents
from profiles.models import UserProfile
from profiles.forms import UserProfileForm
import stripe
import json

@require_POST
def cache_checkout_data(request):
    """ Store bag contents in Stripe metadata before payment """
    try:
        pid = request.POST.get('client_secret').split('_secret')[0]
        stripe.api_key = settings.STRIPE_SECRET_KEY
        stripe.PaymentIntent.modify(pid, metadata={
            'bag': json.dumps(request.session.get('bag', {})),
            'save_info': request.POST.get('save_info'),
            'username': request.user,
        })
        return HttpResponse(status=200)
    except Exception as e:
        messages.error(request, 'Sorry, your payment cannot be processed right now. Please try again later.')
        return HttpResponse(content=e, status=400)

def checkout(request):
    """ Handle the checkout process """
    stripe_public_key = settings.STRIPE_PUBLIC_KEY
    stripe_secret_key = settings.STRIPE_SECRET_KEY

    if not stripe_public_key:
        messages.warning(request, "Stripe public key is missing. Payment processing might not work.")

    if request.method == 'POST':
        bag = request.session.get('bag', {})
        if not bag:
            messages.error(request, "There's nothing in your bag.")
            return redirect(reverse('products'))

        # Handle form submission (e.g., create an order)
        # Add your order processing logic here...

    else:  # GET request (initial page load)
        bag = request.session.get('bag', {})
        if not bag:
            messages.error(request, "There's nothing in your bag at the moment")
            return redirect(reverse('products'))

        current_bag = bag_contents(request)
        total = current_bag['grand_total']

        # ✅ **Create a Stripe PaymentIntent**
        stripe.api_key = stripe_secret_key
        intent = stripe.PaymentIntent.create(
            amount=int(total * 100),  # Stripe expects amount in cents
            currency="eur"
        )

        context = {
            'order_form': OrderForm(),
            'stripe_public_key': stripe_public_key,  # ✅ Pass to template
            'client_secret': intent.client_secret,  # ✅ Pass to template
        }

        return render(request, 'checkout/checkout.html', context)

def checkout_success(request, order_number):
    """ Handle successful checkouts """
    save_info = request.session.get('save_info')
    order = get_object_or_404(Order, order_number=order_number)

    if request.user.is_authenticated:
        profile = UserProfile.objects.get(user=request.user)
        order.user_profile = profile
        order.save()

        if save_info:
            profile_data = {
                'default_phone_number': order.phone_number,
                'default_country': order.country,
                'default_postcode': order.postcode,
                'default_town_or_city': order.town_or_city,
                'default_street_address1': order.street_address1,
                'default_street_address2': order.street_address2,
                'default_county': order.county,
            }
            user_profile_form = UserProfileForm(profile_data, instance=profile)
            if user_profile_form.is_valid():
                user_profile_form.save()

    messages.success(request, f'Order successfully processed! Your order number is {order_number}. A confirmation email will be sent to {order.email}.')

    if 'bag' in request.session:
        del request.session['bag']

    return render(request, 'checkout/checkout_success.html', {'order': order})
