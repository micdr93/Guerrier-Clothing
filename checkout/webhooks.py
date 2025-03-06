import stripe, json
from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from .models import Order, OrderLineItem, Product, UserProfile

@csrf_exempt
def webhook(request):
    wh_secret = settings.STRIPE_WEBHOOK_SECRET
    stripe.api_key = settings.STRIPE_SECRET_KEY
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, wh_secret)
    except stripe.error.SignatureVerificationError:
        return HttpResponseBadRequest("Invalid signature")
    except Exception as e:
        return HttpResponseBadRequest(f"Error parsing webhook: {e}")
    event_type = event['type']
    if event_type == 'payment_intent.succeeded':
        intent = event.data.object
        pid = intent.id
        billing_details = intent.charges.data[0].billing_details
        shipping_details = intent.shipping
        metadata = intent.metadata
        profile = None
        username = metadata.get('username')
        if username and username != "AnonymousUser":
            profile = UserProfile.objects.get(user__username=username)
        try:
            order = Order.objects.get(stripe_pid=pid)
        except Order.DoesNotExist:
            try:
                order = Order.objects.create(
                    full_name=shipping_details.name,
                    user_profile=profile,
                    email=billing_details.email,
                    phone_number=shipping_details.phone or "",
                    country=shipping_details.address.country or "",
                    postcode=shipping_details.address.postal_code or "",
                    town_or_city=shipping_details.address.city or "",
                    street_address1=shipping_details.address.line1 or "",
                    street_address2=shipping_details.address.line2 or "",
                    county=shipping_details.address.state or "",
                    original_bag=metadata.get('bag', "{}"),
                    stripe_pid=pid,
                )
                bag = json.loads(metadata.get('bag', '{}'))
                for item_id, item_data in bag.items():
                    product = Product.objects.get(id=item_id)
                    if isinstance(item_data, int):
                        OrderLineItem.objects.create(order=order, product=product, quantity=item_data)
                    else:
                        for option, quantity in item_data.items():
                            OrderLineItem.objects.create(order=order, product=product, quantity=quantity, option=option)
            except Exception as e:
                if order:
                    order.delete()
                return HttpResponse(f"Webhook received: {event_type} | ERROR: {e}", status=500)
        return HttpResponse(f"Webhook received: {event_type}", status=200)
    elif event_type == 'payment_intent.payment_failed':
        return HttpResponse(f"Webhook received: {event_type} | Payment failed", status=200)
    else:
        return HttpResponse(f"Webhook received: {event_type} | Unhandled event type", status=200)
