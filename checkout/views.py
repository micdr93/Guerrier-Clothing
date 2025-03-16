import json
import stripe
from django.shortcuts import render, redirect, reverse, get_object_or_404, HttpResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings

from .forms import OrderForm
from .models import Order, OrderLineItem
from bag.contexts import bag_contents  # Required to compute totals
from products.models import Product
from profiles.models import UserProfile
from profiles.forms import UserProfileForm


@require_POST
def cache_checkout_data(request):
    """
    Cache checkout data in Stripe PaymentIntent metadata
    """
    try:
        client_secret = request.POST.get('client_secret')
        if not client_secret:
            return HttpResponse("Missing client_secret", status=400)
        pid = client_secret.split('_secret')[0]

        stripe.api_key = settings.STRIPE_SECRET_KEY
        stripe.PaymentIntent.modify(pid, metadata={
            'bag': json.dumps(request.session.get('bag', {})),
            'save_info': request.POST.get('save_info'),
            'username': request.user.username if request.user.is_authenticated else 'AnonymousUser',
        })
        return HttpResponse(status=200)

    except Exception as e:
        messages.error(request, "Payment processing error. Please try again.")
        return HttpResponse(content=str(e), status=400)


def checkout(request):
    """
    Handles the checkout process.
    """
    stripe_public_key = settings.STRIPE_PUBLIC_KEY
    stripe_secret_key = settings.STRIPE_SECRET_KEY

    if request.method == "POST":
        bag = request.session.get("bag", {})

        form_data = {
            "full_name": request.POST["full_name"],
            "email": request.POST["email"],
            "phone_number": request.POST["phone_number"],
            "country": request.POST["country"],
            "postcode": request.POST["postcode"],
            "town_or_city": request.POST["town_or_city"],
            "street_address1": request.POST["street_address1"],
            "street_address2": request.POST["street_address2"],
            "county": request.POST["county"],
        }

        order_form = OrderForm(form_data)
        if order_form.is_valid():
            order = order_form.save(commit=False)
            order.original_bag = json.dumps(bag)
            order.save()

            # Create PaymentIntent
            current_bag = bag_contents(request)
            total = current_bag["grand_total"]
            stripe_total = round(total * 100)

            intent = stripe.PaymentIntent.create(
                amount=stripe_total,
                currency=settings.STRIPE_CURRENCY,
                payment_method_types=["card"],
            )

            request.session["save_info"] = "save-info" in request.POST

            context = {
                "order_form": order_form,
                "stripe_public_key": stripe_public_key,
                "client_secret": intent.client_secret,
            }
            return render(request, "checkout/checkout.html", context)

    else:
        bag = request.session.get("bag", {})
        if not bag:
            messages.error(request, "Your shopping bag is empty.")
            return redirect(reverse("products"))

        current_bag = bag_contents(request)
        total = current_bag["grand_total"]
        stripe_total = round(total * 100)

        intent = stripe.PaymentIntent.create(
            amount=stripe_total,
            currency=settings.STRIPE_CURRENCY,
            payment_method_types=["card"],
        )

        context = {
            "order_form": OrderForm(),
            "stripe_public_key": stripe_public_key,
            "client_secret": intent.client_secret,
        }
        return render(request, "checkout/checkout.html", context)


def checkout_success(request, order_number):
    """
    Handles successful checkouts, updates order status, and sends confirmation email.
    """
    order = get_object_or_404(Order, order_number=order_number)
    order.paid = True
    order.save()

    # Send confirmation email
    subject = f'Order Confirmation - {order.order_number}'
    message = f'Thank you for your purchase! Your order details:\n\n{order}'
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [order.email],
    )

    if 'bag' in request.session:
        del request.session['bag']

    return render(request, 'checkout/checkout_success.html', {'order': order})

def order_detail(request, order_number):
    """
    Displays detailed information for a specific order.
    """
    order = get_object_or_404(Order, order_number=order_number)
    return render(request, 'checkout/order_detail.html', {'order': order})