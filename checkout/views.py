import json
import stripe
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib import messages
from django.conf import settings
from django.views.decorators.http import require_POST
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .forms import OrderForm
from .models import Order, OrderLineItem
from products.models import Product
from bag.contexts import bag_contents
from profiles.models import UserProfile
from profiles.forms import UserProfileForm
from .utils import send_confirmation_email, convert_country

@require_POST
def cache_checkout_data(request):
    try:
        client_secret = request.POST.get('client_secret')
        pid = client_secret.split('_secret')[0]
        stripe.api_key = settings.STRIPE_SECRET_KEY
        stripe.PaymentIntent.modify(pid, metadata={
            'bag': json.dumps(request.session.get('bag', {})),
            'save_info': request.POST.get('save_info'),
            'username': request.user if request.user.is_authenticated else 'AnonymousUser',
        })
        return HttpResponse(status=200)
    except Exception as e:
        messages.error(
            request,
            'Sorry, your payment cannot be processed right now. Please try again later.'
        )
        return HttpResponse(content=str(e), status=400)

def checkout(request):
    stripe_public_key = settings.STRIPE_PUBLIC_KEY
    stripe_secret_key = settings.STRIPE_SECRET_KEY
    stripe.api_key = stripe_secret_key

    if request.method == 'POST':
        bag = request.session.get('bag', {})
        form_data = {
            'full_name': request.POST.get('full_name'),
            'email': request.POST.get('email'),
            'phone_number': request.POST.get('phone_number'),
            'country': request.POST.get('country'),
            'postcode': request.POST.get('postcode'),
            'town_or_city': request.POST.get('town_or_city'),
            'street_address1': request.POST.get('street_address1'),
            'street_address2': request.POST.get('street_address2'),
            'county': request.POST.get('county'),
        }
        order_form = OrderForm(form_data)
        client_secret = request.POST.get('client_secret')
        if not client_secret:
            messages.error(request, "Payment information is missing. Please try again.")
            return redirect(reverse('checkout:checkout'))

        if order_form.is_valid():
            current_bag = bag_contents(request)
            order = order_form.save(commit=False)
            order.country = convert_country(order.country)
            pid = client_secret.split('_secret')[0]
            order.stripe_pid = pid
            order.original_bag = json.dumps(bag)
            order.order_total = current_bag.get('total')
            order.delivery_cost = current_bag.get('delivery')
            order.grand_total = current_bag.get('grand_total')
            if request.user.is_authenticated:
                profile = UserProfile.objects.get(user=request.user)
                order.user_profile = profile
            order.save()

            for item_id, item_data in bag.items():
                product = Product.objects.get(id=item_id)
                if isinstance(item_data, int):
                    OrderLineItem.objects.create(
                        order=order,
                        product=product,
                        quantity=item_data
                    )
                else:
                    for option, quantity in item_data.items():
                        OrderLineItem.objects.create(
                            order=order,
                            product=product,
                            quantity=quantity,
                            option=option
                        )

            # Save the "save_info" flag in session
            request.session['save_info'] = 'save_info' in request.POST

            return redirect(reverse('checkout:checkout_success', args=[order.order_number]))
        else:
            messages.error(request, "There was an error with your form. Please double-check your information.")
            # Fall through to re-render the form below

    # GET request or if POST fails:
    bag = request.session.get('bag', {})
    if not bag:
        messages.error(request, "There's nothing in your bag at the moment.")
        return redirect(reverse('products'))

    current_bag = bag_contents(request)
    total = current_bag.get('grand_total', 0)
    stripe_total = round(total * 100)
    # Create a PaymentIntent dynamically
    intent = stripe.PaymentIntent.create(
        amount=stripe_total,
        currency=getattr(settings, 'STRIPE_CURRENCY', 'eur'),
        metadata={
            'bag': json.dumps(bag),
            'username': request.user.username if request.user.is_authenticated else 'AnonymousUser'
        }
    )

    if request.user.is_authenticated:
        try:
            profile = UserProfile.objects.get(user=request.user)
            order_form = OrderForm(initial={
                'full_name': profile.user.get_full_name(),
                'email': profile.user.email,
                'phone_number': profile.default_phone_number,
                'country': profile.default_country,
                'postcode': profile.default_postcode,
                'town_or_city': profile.default_town_or_city,
                'street_address1': profile.default_street_address1,
                'street_address2': profile.default_street_address2,
                'county': profile.default_county,
            })
        except UserProfile.DoesNotExist:
            order_form = OrderForm()
    else:
        order_form = OrderForm()

    context = {
        'order_form': order_form,
        'stripe_public_key': stripe_public_key,
        'client_secret': intent.client_secret,
        'bag': bag,
        'all_products': {item_id: Product.objects.get(id=item_id) for item_id in bag},
        'total': current_bag.get('total', 0),
        'delivery': current_bag.get('delivery', 0),
        'grand_total': total,
    }
    template = 'checkout/checkout.html'
    return render(request, template, context)

def checkout_success(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)
    send_confirmation_email(order)
    messages.success(
        request,
        f'Order successfully processed! Your order number is {order_number}. A confirmation email has been sent to {order.email}.'
    )
    if 'bag' in request.session:
        del request.session['bag']
    return render(request, 'checkout/checkout_success.html', {'order': order})

@login_required
def order_detail(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)
    if order.user_profile and order.user_profile.user != request.user:
        return render(request, '403.html', status=403)
    return render(request, 'checkout/order_detail.html', {'order': order})
