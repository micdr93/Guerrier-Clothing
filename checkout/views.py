import json
import stripe
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib import messages
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

from bag.contexts import bag_contents
from products.models import Product
from profiles.models import UserProfile
from profiles.forms import UserProfileForm
from .forms import OrderForm
from .models import Order, OrderLineItem
from .utils import send_confirmation_email

def checkout(request):
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
            pid = request.POST.get("client_secret").split("_secret")[0]
            order.stripe_pid = pid
            order.original_bag = json.dumps(bag)
            order.save()
            for item_id, item_data in bag.items():
                try:
                    product = Product.objects.get(id=item_id)
                    if isinstance(item_data, int):
                        order_line_item = OrderLineItem(
                            order=order,
                            product=product,
                            quantity=item_data,
                        )
                        order_line_item.save()
                    else:
                        for size, quantity in item_data.items():
                            if size != 'DEFAULT':
                                order_line_item = OrderLineItem(
                                    order=order,
                                    product=product,
                                    quantity=quantity,
                                    product_size=size,
                                )
                                order_line_item.save()
                except Product.DoesNotExist:
                    messages.error(
                        request,
                        (
                            "One of the products in your bag wasn't found in our database. "
                            "Please call us for assistance!"
                        ),
                    )
                    order.delete()
                    return redirect(reverse("bag:view_bag"))

            request.session["save_info"] = "save-info" in request.POST
            return redirect(
                reverse("checkout:checkout_success", args=[order.order_number])
            )
        else:
            messages.error(
                request,
                "There was an error with your form. Please double check your information.",
            )
    else:
        bag = request.session.get("bag", {})
        if not bag:
            messages.error(request, "There's nothing in your bag at the moment")
            return redirect(reverse("products:products"))

        current_bag = bag_contents(request)
        total = current_bag["grand_total"]
        stripe_total = round(total * 100)
        stripe.api_key = stripe_secret_key
        intent = stripe.PaymentIntent.create(
            amount=stripe_total,
            currency=settings.STRIPE_CURRENCY,
        )

        # Prepare bag items with subtotals
        bag_items = []
        for item_id, item_data in bag.items():
            try:
                product = Product.objects.get(id=item_id)
                
                if isinstance(item_data, int):
                    bag_items.append({
                        'product': product,
                        'quantity': item_data,
                        'size': None,
                        'price': product.price,
                    })
                else:
                    for size, quantity in item_data.items():
                        if size != 'DEFAULT':
                            bag_items.append({
                                'product': product,
                                'quantity': quantity,
                                'size': size,
                                'price': product.price,
                            })
            except Product.DoesNotExist:
                continue

        if request.user.is_authenticated:
            try:
                profile = UserProfile.objects.get(user=request.user)
                order_form = OrderForm(
                    initial={
                        "full_name": profile.user.get_full_name(),
                        "email": profile.user.email,
                        "phone_number": profile.default_phone_number,
                        "country": profile.default_country,
                        "postcode": profile.default_postcode,
                        "town_or_city": profile.default_town_or_city,
                        "street_address1": profile.default_street_address1,
                        "street_address2": profile.default_street_address2,
                        "county": profile.default_county,
                    }
                )
            except UserProfile.DoesNotExist:
                order_form = OrderForm()
        else:
            order_form = OrderForm()

        if not stripe_public_key:
            stripe_public_key = settings.STRIPE_PUBLIC_KEY
            messages.warning(
                request,
                "Stripe public key is missing. Did you forget to set it in your environment?",
            )

        template = "checkout/checkout.html"
        context = {
            "order_form": order_form,
            "stripe_public_key": stripe_public_key,
            "client_secret": intent.client_secret,
            "bag_items": bag_items,
            "total": total,
            "product_count": len(bag_items),
            "delivery": current_bag["delivery"],
            "grand_total": current_bag["grand_total"],
        }

        return render(request, template, context)

@require_POST
@csrf_exempt
def cache_checkout_data(request):
    try:
        pid = request.POST.get("client_secret").split("_secret")[0]
        stripe.api_key = settings.STRIPE_SECRET_KEY

        metadata = {
            "username": (
                request.user.username
                if request.user.is_authenticated
                else "AnonymousUser"
            ),
        }

        if "bag" in request.session:
            metadata["bag"] = json.dumps(request.session.get("bag", {}))

        if "save_info" in request.POST:
            metadata["save_info"] = request.POST.get("save_info")

        stripe.PaymentIntent.modify(pid, metadata=metadata)

        return HttpResponse(status=200)
    except Exception as e:
        print(f"STRIPE ERROR: {str(e)}")
        return HttpResponse(content=str(e), status=400)

def checkout_success(request, order_number):
    save_info = request.session.get("save_info")
    order = get_object_or_404(Order, order_number=order_number)

    if request.user.is_authenticated:
        try:
            profile = UserProfile.objects.get(user=request.user)
            order.user_profile = profile
            order.save()

            if save_info:
                profile_data = {
                    "default_phone_number": order.phone_number,
                    "default_country": order.country,
                    "default_postcode": order.postcode,
                    "default_town_or_city": order.town_or_city,
                    "default_street_address1": order.street_address1,
                    "default_street_address2": order.street_address2,
                    "default_county": order.county,
                }
                user_profile_form = UserProfileForm(profile_data, instance=profile)
                if user_profile_form.is_valid():
                    user_profile_form.save()
        except UserProfile.DoesNotExist:
            pass

    try:
        send_confirmation_email(order)
    except Exception as e:
        messages.error(
            request,
            f"Order confirmed, but we had an issue sending your confirmation email. Error: {e}",
        )

    messages.success(
        request,
        f"Order successfully processed! Your order number is {order_number}. A confirmation email will be sent to {order.email}.",
    )

    if "bag" in request.session:
        del request.session["bag"]

    template = "checkout/checkout_success.html"
    context = {
        "order": order,
    }

    return render(request, template, context)

def order_detail(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)

    if request.user.is_authenticated:
        profile = UserProfile.objects.get(user=request.user)
        if order.user_profile == profile:
            template = "checkout/order_detail.html"
            context = {
                "order": order,
                "from_profile": False,
            }
            return render(request, template, context)
        else:
            messages.error(request, "You don't have permission to view this order.")
            return redirect(reverse("home"))
    else:
        messages.error(request, "Please log in to view this order.")
        return redirect(reverse("account_login"))