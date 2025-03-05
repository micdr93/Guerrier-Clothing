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
from django.contrib.auth.decorators import login_required
from profiles.forms import UserProfileForm
import stripe
import json
from django.db.models import Sum
import os

@require_POST
def cache_checkout_data(request):
    try:
        pid = request.POST.get('client_secret').split('_secret')[0]
        stripe.api_key = settings.STRIPE_SECRET_KEY
        stripe.PaymentIntent.modify(pid, metadata={
            'bag': json.dumps(request.session.get('bag', {})),
            'save_info': request.POST.get('save_info'),
            'username': request.user.username if request.user.is_authenticated else 'Anonymous',
        })
        return HttpResponse(status=200)
    except Exception as e:
        messages.error(request, 'Sorry, your payment cannot be processed right now. Please try again later.')
        return HttpResponse(content=str(e), status=400)

def checkout(request):
    stripe_public_key = settings.STRIPE_PUBLIC_KEY
    stripe_secret_key = settings.STRIPE_SECRET_KEY
    stripe.api_key = stripe_secret_key

    if stripe_secret_key:
        key_preview = stripe_secret_key[:6] + "..." if len(stripe_secret_key) > 6 else "NOT SET"
        print(f"🔑 Using Stripe Secret Key: {key_preview}")

    if not stripe_public_key or not stripe_secret_key:
        messages.error(request, "Stripe API keys are missing. Please check your environment variables.")

    if request.method == 'POST':
        bag = request.session.get('bag', {})
        if not bag:
            messages.error(request, "There's nothing in your bag.")
            return redirect(reverse('products'))

        form_data = {
            'full_name': request.POST.get('full_name'),
            'email': request.POST.get('email'),
            'phone_number': request.POST.get('phone_number'),
            'country': request.POST.get('country'),
            'postcode': request.POST.get('postcode'),
            'town_or_city': request.POST.get('town_or_city'),
            'street_address1': request.POST.get('street_address1'),
            'street_address2': request.POST.get('street_address2'),
        }

        order_form = OrderForm(form_data)

        if order_form.is_valid():
            try:
                order = order_form.save(commit=False)
                pid = request.POST.get('client_secret', '')
                if pid:
                    order.stripe_pid = pid.split('_secret')[0]
                if request.user.is_authenticated:
                    try:
                        profile = UserProfile.objects.get(user=request.user)
                        order.user_profile = profile
                        print(f"✅ Order associated with user profile: {profile}")
                    except UserProfile.DoesNotExist:
                        print(f"❌ No user profile found for user: {request.user.username}")

                current_bag = bag_contents(request)
                order.delivery_cost = current_bag.get('delivery', 0)
                order.order_total = current_bag.get('total', 0)
                order.grand_total = current_bag.get('grand_total', 0)
                order.save()

                for item_id, quantity in bag.items():
                    try:
                        product = Product.objects.get(id=item_id)
                        line_item = OrderLineItem(
                            order=order,
                            product=product,
                            quantity=quantity,
                        )
                        line_item.lineitem_total = product.price * quantity
                        line_item.save()
                    except Product.DoesNotExist:
                        messages.error(request, f"Product {item_id} not found")
                        order.delete()
                        return redirect(reverse('bag:view_bag'))

                request.session['bag'] = {}
                # Use the proper namespace for checkout_success
                return redirect(reverse('checkout:checkout_success', args=[order.order_number]))

            except Exception as e:
                print(f"ERROR: {type(e).__name__}: {str(e)}")
                messages.error(request, f"There was an error processing your order: {str(e)}")
                return redirect(reverse('bag:view_bag'))
        else:
            messages.error(request, "There was an error with your form. Please check your information.")
    else:
        bag = request.session.get('bag', {})
        if not bag:
            messages.error(request, "There's nothing in your bag at the moment")
            return redirect(reverse('products'))

        current_bag = bag_contents(request)
        total = current_bag.get('grand_total')

        if total is None:
            messages.error(request, "Something went wrong calculating your order total.")
            return redirect(reverse('bag:view_bag'))

        try:
            intent = stripe.PaymentIntent.create(
                amount=int(total * 100),
                currency="eur"
            )
            print(f"✅ Stripe PaymentIntent Created: {intent.id}")
            client_secret = intent.client_secret
        except Exception as e:
            print(f"❌ Stripe Error: {str(e)}")
            messages.error(request, "Stripe payment could not be initialized.")
            return redirect(reverse('bag:view_bag'))

        order_form = OrderForm()

    # Get all products in the bag to display images
    bag = request.session.get('bag', {})
    all_products = {}
    for item_id in bag:
        try:
            product = Product.objects.get(id=item_id)
            all_products[item_id] = product
        except Product.DoesNotExist:
            pass

    context = {
        'order_form': order_form,
        'stripe_public_key': stripe_public_key,
        'client_secret': client_secret,
        'bag': bag,
        'all_products': all_products,
        'total': current_bag.get('total', 0),
        'delivery': current_bag.get('delivery', 0),
        'grand_total': current_bag.get('grand_total', 0),
    }
    return render(request, 'checkout/checkout.html', context)

def checkout_success(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)
    print(f"🛒 Order Number: {order.order_number}")
    print(f"👤 User Profile: {order.user_profile}")
    if request.user.is_authenticated:
        print(f"🔐 Logged in User: {request.user.username}")
    
    messages.success(
        request,
        f'Order successfully processed! Your order number is {order_number}. A confirmation email will be sent to {order.email}.'
    )
    
    # Clear the bag once the order is successful
    if 'bag' in request.session:
        del request.session['bag']
    
    # Render the checkout success template instead of redirecting to avoid redirect loops.
    return render(request, 'checkout/checkout_success.html', {'order': order})

@login_required
def order_detail(request, order_number):
    """
    Display the details of a single order.
    Ensure the order belongs to the current user.
    """
    order = get_object_or_404(Order, order_number=order_number)
    if order.user_profile and order.user_profile.user != request.user:
        return render(request, '403.html', status=403)
    return render(request, 'checkout/order_detail.html', {'order': order})