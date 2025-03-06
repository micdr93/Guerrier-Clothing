import stripe, json
from django.conf import settings
from .models import Order, OrderLineItem, Product, UserProfile

def handle_stripe_event(event):
    event_type = event.get('type')
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
            order = None
        if order:
            return order
        else:
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
                raise e
            return order
    elif event_type == 'payment_intent.payment_failed':
        return None
    else:
        return None
