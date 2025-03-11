import json
import time
import stripe
from django.http import HttpResponse
from django.conf import settings
from .models import Order, OrderLineItem
from products.models import Product
from profiles.models import UserProfile
from .utils import send_confirmation_email, convert_country


@require_POST
@csrf_exempt
def webhook(request):
    """Listen for webhooks from Stripe"""
    # Setup
    wh_secret = settings.STRIPE_WEBHOOK_SECRET
    stripe.api_key = settings.STRIPE_SECRET_KEY

    # Debug logging
    print(f"Webhook secret first 5 chars: {wh_secret[:5] if wh_secret else 'None'}")
    print(f"Webhook secret length: {len(wh_secret) if wh_secret else 0}")

    # Get the webhook data and verify its signature
    payload = request.body
    print(f"Payload length: {len(payload)}")

    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")
    print(f"Signature header present: {sig_header is not None}")
    print(
        f"Signature header first 10 chars: {sig_header[:10] if sig_header else 'None'}"
    )

    # Debug for request headers
    stripe_headers = [
        k for k in request.META.keys() if k.startswith("HTTP_") and "STRIPE" in k
    ]
    print(f"Stripe-related headers: {stripe_headers}")

    event = None

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, wh_secret)
        print("✅ Webhook signature verification successful")
    except ValueError as e:
        print(f"❌ Invalid payload: {str(e)}")
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        print(f"❌ Invalid signature: {str(e)}")
        return HttpResponse(status=400)
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return HttpResponse(content=str(e), status=400)


class StripeWH_Handler:
    def __init__(self, request):
        self.request = request

    def handle_event(self, event):
        return HttpResponse(
            content=f'Unhandled webhook received: {event["type"]}', status=200
        )

    def handle_payment_intent_succeeded(self, event):
        intent = event.data.object
        pid = intent.id
        bag = intent.metadata.get("bag", {})
        save_info = intent.metadata.get("save_info")
        stripe_charge = stripe.Charge.retrieve(intent.latest_charge)
        billing_details = stripe_charge.billing_details
        shipping_details = intent.shipping
        grand_total = round(stripe_charge.amount / 100, 2)
        for field, value in shipping_details.address.items():
            if value == "":
                shipping_details.address[field] = None
        country_code = convert_country(shipping_details.address.country)
        profile = None
        username = intent.metadata.get("username")
        if username != "AnonymousUser":
            profile = UserProfile.objects.get(user__username=username)
            if save_info:
                profile.default_phone_number = shipping_details.phone
                profile.default_country = country_code
                profile.default_postcode = shipping_details.address.postal_code
                profile.default_town_or_city = shipping_details.address.city
                profile.default_street_address1 = shipping_details.address.line1
                profile.default_street_address2 = shipping_details.address.line2
                profile.default_county = shipping_details.address.state
                profile.save()
        order_exists = False
        attempt = 1
        while attempt <= 5:
            try:
                order = Order.objects.get(
                    full_name__iexact=shipping_details.name,
                    email__iexact=billing_details.email,
                    phone_number__iexact=shipping_details.phone,
                    country__iexact=country_code,
                    postcode__iexact=shipping_details.address.postal_code,
                    town_or_city__iexact=shipping_details.address.city,
                    street_address1__iexact=shipping_details.address.line1,
                    street_address2__iexact=shipping_details.address.line2,
                    county__iexact=shipping_details.address.state,
                    grand_total=grand_total,
                    original_bag=bag,
                    stripe_pid=pid,
                )
                order_exists = True
                break
            except Order.DoesNotExist:
                attempt += 1
                time.sleep(1)
        if order_exists:
            send_confirmation_email(order)
            return HttpResponse(
                content=f'Webhook received: {event["type"]} | SUCCESS: Verified order already in database',
                status=200,
            )
        else:
            order = None
            try:
                order = Order.objects.create(
                    full_name=shipping_details.name,
                    user_profile=profile,
                    email=billing_details.email,
                    phone_number=shipping_details.phone,
                    country=country_code,
                    postcode=shipping_details.address.postal_code,
                    town_or_city=shipping_details.address.city,
                    street_address1=shipping_details.address.line1,
                    street_address2=shipping_details.address.line2,
                    county=shipping_details.address.state,
                    original_bag=bag,
                    stripe_pid=pid,
                )
                for item_id, item_data in json.loads(bag).items():
                    product = Product.objects.get(id=item_id)
                    if isinstance(item_data, int):
                        order_line_item = OrderLineItem(
                            order=order, product=product, quantity=item_data
                        )
                        order_line_item.save()
                    else:
                        for size, quantity in item_data["items_by_size"].items():
                            order_line_item = OrderLineItem(
                                order=order,
                                product=product,
                                quantity=quantity,
                                product_size=size,
                            )
                            order_line_item.save()
            except Exception as e:
                if order:
                    order.delete()
                return HttpResponse(
                    content=f'Webhook received: {event["type"]} | ERROR: {e}',
                    status=500,
                )
            send_confirmation_email(order)
            return HttpResponse(
                content=f'Webhook received: {event["type"]} | SUCCESS: Created order in webhook',
                status=200,
            )

    def handle_payment_intent_payment_failed(self, event):
        return HttpResponse(content=f'Webhook received: {event["type"]}', status=200)
