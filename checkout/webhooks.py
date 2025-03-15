import json
import stripe
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .webhooks_handler import StripeWH_Handler

@csrf_exempt
def webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = settings.STRIPE_WH_SECRET
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except Exception:
        return HttpResponse(status=400)
    handler = StripeWH_Handler(request)
    event_type = event['type']
    if event_type == 'payment_intent.succeeded':
        response = handler.handle_payment_intent_succeeded(event)
    elif event_type == 'payment_intent.payment_failed':
        response = handler.handle_payment_intent_payment_failed(event)
    else:
        response = handler.handle_event(event)
    return response
