import stripe
import json
import time
from django.http import HttpResponse
from django.conf import settings
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

from .models import Order, OrderLineItem
from products.models import Product
from profiles.models import UserProfile
from .utils import send_confirmation_email

@require_POST
@csrf_exempt
def webhook(request):
    """Listen for webhooks from Stripe"""
    # Setup
    wh_secret = settings.STRIPE_WEBHOOK_SECRET
    stripe.api_key = settings.STRIPE_SECRET_KEY

    # Get the webhook data and verify its signature
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, wh_secret
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)
    except Exception as e:
        return HttpResponse(content=str(e), status=400)

    # Handle different webhook events
    event_type = event['type']
    
    if event_type == 'payment_intent.succeeded':
        payment_intent = event.data.object
        
        try:
            order = Order.objects.get(stripe_pid=payment_intent.id)
            # Order exists, so just send the confirmation email
            send_confirmation_email(order)
            return HttpResponse(
                content=f'Webhook received: {event_type} | SUCCESS: Order found in database',
                status=200)
        except Order.DoesNotExist:
            # Order doesn't exist, so we'll need to create it
            try:
                # Extract order information from payment intent
                bag = json.loads(payment_intent.metadata.get('bag', '{}'))
                shipping_details = payment_intent.shipping
                billing_details = payment_intent.charges.data[0].billing_details
                grand_total = round(payment_intent.amount / 100, 2)
                
                # Create user profile if user is authenticated
                profile = None
                username = payment_intent.metadata.get('username')
                if username != 'AnonymousUser':
                    profile = UserProfile.objects.get(user__username=username)

                # Create the order
                order = Order.objects.create(
                    full_name=shipping_details.name,
                    user_profile=profile,
                    email=billing_details.email,
                    phone_number=shipping_details.phone,
                    country=shipping_details.address.country,
                    postcode=shipping_details.address.postal_code,
                    town_or_city=shipping_details.address.city,
                    street_address1=shipping_details.address.line1,
                    street_address2=shipping_details.address.line2,
                    county=shipping_details.address.state,
                    original_bag=payment_intent.metadata.get('bag'),
                    stripe_pid=payment_intent.id,
                )
                
                # Create order line items
                for item_id, item_data in bag.items():
                    product = Product.objects.get(id=item_id)
                    if isinstance(item_data, int):
                        order_line_item = OrderLineItem(
                            order=order,
                            product=product,
                            quantity=item_data,
                        )
                        order_line_item.save()
                    else:
                        for option, quantity in item_data.items():
                            order_line_item = OrderLineItem(
                                order=order,
                                product=product,
                                quantity=quantity,
                                option=option,
                            )
                            order_line_item.save()
                
                # Send confirmation email
                send_confirmation_email(order)
                
                return HttpResponse(
                    content=f'Webhook received: {event_type} | SUCCESS: Created order in webhook',
                    status=200)
                    
            except Exception as e:
                # If there's an error, delete the order if it was created
                if 'order' in locals():
                    order.delete()
                return HttpResponse(
                    content=f'Webhook received: {event_type} | ERROR: {str(e)}',
                    status=500)
                    
    elif event_type == 'payment_intent.payment_failed':
        return HttpResponse(
            content=f'Webhook received: {event_type} | Payment Failed',
            status=200)
            
    else:
        return HttpResponse(
            content=f'Webhook received: {event_type} | Unhandled event',
            status=200)