import stripe
import json
import time
import logging
from django.http import HttpResponse
from django.conf import settings
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

from .models import Order, OrderLineItem
from products.models import Product
from profiles.models import UserProfile
from .utils import send_confirmation_email

logger = logging.getLogger(__name__)

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
        logger.error(f"Invalid Stripe webhook payload: {str(e)}")
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        logger.error(f"Invalid Stripe webhook signature: {str(e)}")
        return HttpResponse(status=400)
    except Exception as e:
        logger.error(f"Stripe webhook error: {str(e)}")
        return HttpResponse(content=str(e), status=400)

    # Handle different webhook events
    event_type = event['type']
    logger.info(f"Webhook received: {event_type}")
    
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
                bag_json = payment_intent.metadata.get('bag', '{}')
                bag = json.loads(bag_json)
                shipping_details = payment_intent.shipping
                
                # Handle billing details based on the webhook structure
                if hasattr(payment_intent, 'charges') and payment_intent.charges.data:
                    billing_details = payment_intent.charges.data[0].billing_details
                else:
                    # For test events or older API versions
                    try:
                        stripe_charge = stripe.Charge.retrieve(payment_intent.latest_charge)
                        billing_details = stripe_charge.billing_details
                    except Exception as e:
                        logger.error(f"Could not retrieve charge details: {str(e)}")
                        billing_details = shipping_details  # Fallback to shipping details
                
                grand_total = round(payment_intent.amount / 100, 2)
                
                # Create user profile if user is authenticated
                profile = None
                username = payment_intent.metadata.get('username')
                if username and username != 'AnonymousUser':
                    try:
                        profile = UserProfile.objects.get(user__username=username)
                    except UserProfile.DoesNotExist:
                        logger.warning(f"UserProfile not found for username: {username}")
                
                # Clean up empty strings in shipping details
                shipping_address = shipping_details.address.to_dict() if hasattr(shipping_details.address, 'to_dict') else shipping_details.address
                for field, value in shipping_address.items():
                    if value == "":
                        shipping_address[field] = None

                # Create the order
                order = Order.objects.create(
                    full_name=shipping_details.name,
                    user_profile=profile,
                    email=billing_details.email,
                    phone_number=shipping_details.phone,
                    country=shipping_address.get('country'),
                    postcode=shipping_address.get('postal_code'),
                    town_or_city=shipping_address.get('city'),
                    street_address1=shipping_address.get('line1'),
                    street_address2=shipping_address.get('line2'),
                    county=shipping_address.get('state'),
                    original_bag=bag_json,
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
                        # Handle items with options (like size)
                        if 'items_by_size' in item_data:
                            for size, quantity in item_data['items_by_size'].items():
                                order_line_item = OrderLineItem(
                                    order=order,
                                    product=product,
                                    quantity=quantity,
                                    product_size=size,  # Ensure this field exists in your model
                                )
                                order_line_item.save()
                        else:
                            # Generic option handling
                            for option, quantity in item_data.items():
                                order_line_item = OrderLineItem(
                                    order=order,
                                    product=product,
                                    quantity=quantity,
                                )
                                order_line_item.save()
                
                # Update order totals
                order.update_total()
                
                # Send confirmation email
                send_confirmation_email(order)
                
                return HttpResponse(
                    content=f'Webhook received: {event_type} | SUCCESS: Created order in webhook',
                    status=200)
                    
            except Exception as e:
                # If there's an error, delete the order if it was created
                logger.error(f"Webhook order creation error: {str(e)}")
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