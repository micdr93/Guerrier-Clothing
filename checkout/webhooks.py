import json
import stripe
from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from .webhooks_handler import handle_stripe_event

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except ValueError:
        # Invalid payload
        return HttpResponseBadRequest("Invalid payload")
    except stripe.error.SignatureVerificationError:
        # Invalid signature
        return HttpResponseBadRequest("Invalid signature")

    # Process the event using our handler
    response = handle_stripe_event(event)
    return response
