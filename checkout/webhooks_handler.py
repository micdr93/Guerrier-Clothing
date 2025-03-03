from django.http import HttpResponse
from django.contrib import messages

def handle_stripe_event(event):
    event_type = event.get('type')
    data_object = event.get('data', {}).get('object')

    if event_type == 'payment_intent.succeeded':
        # For example: Update your order status or perform post-payment tasks
        print("PaymentIntent succeeded!")
        # Example: order_id = data_object.get('metadata', {}).get('order_id')
        # If you store an order ID in the metadata, you can update the corresponding order here.
    elif event_type == 'payment_intent.payment_failed':
        print("PaymentIntent failed")
        # Handle failure accordingly
    else:
        # Handle any other event types you care about
        print(f"Unhandled event type: {event_type}")

    # Return a 200 response to acknowledge receipt of the event
    return HttpResponse(status=200)
