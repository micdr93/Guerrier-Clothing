import stripe
import json
from django.http import HttpResponse
from django.conf import settings
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

@require_POST
@csrf_exempt
def webhook(request):
    """Listen for webhooks from Stripe"""
    # Setup
    wh_secret = settings.STRIPE_WEBHOOK_SECRET
    stripe.api_key = settings.STRIPE_SECRET_KEY

    # Debug logging - This will show in Heroku logs
    print(f"[WEBHOOK DEBUG] Secret: {wh_secret[:5]}... (length: {len(wh_secret)})")
    
    # Get the webhook data and verify its signature
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    
    print(f"[WEBHOOK DEBUG] Payload length: {len(payload)}")
    print(f"[WEBHOOK DEBUG] Signature header present: {sig_header is not None}")
    
    # List all headers for debugging
    all_headers = {k: v for k, v in request.META.items() if k.startswith('HTTP_')}
    print(f"[WEBHOOK DEBUG] All HTTP headers: {all_headers}")
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, wh_secret
        )
        print(f"[WEBHOOK DEBUG] ✅ Verification successful for event: {event['type']}")
        
        # Always return 200 for testing - we're just trying to get verification working
        return HttpResponse(content=f"Webhook received: {event['type']}", status=200)
        
    except ValueError as e:
        print(f"[WEBHOOK DEBUG] ❌ Invalid payload: {str(e)}")
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        print(f"[WEBHOOK DEBUG] ❌ Invalid signature: {str(e)}")
        return HttpResponse(status=400)
    except Exception as e:
        print(f"[WEBHOOK DEBUG] ❌ Unexpected error: {str(e)}")
        return HttpResponse(content=str(e), status=400)