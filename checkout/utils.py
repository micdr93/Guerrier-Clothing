from django.core.mail import send_mail
from django.conf import settings

def send_confirmation_email(order):
    cust_email = order.email
    subject = f"Guerrier Clothing - Order Confirmation {order.order_number}"
    text_message = f"""
Hello {order.full_name}!

This is a confirmation of your order at Guerrier Clothing. Your order information is below:

Order Number: {order.order_number}
Order Date: {order.date}

Order Total: €{order.order_total}
Delivery: €{order.delivery_cost}
Grand Total: €{order.grand_total}

Your order will be shipped to {order.street_address1} in {order.town_or_city}, {order.country}.

We've got your phone number on file as {order.phone_number}.

If you have any questions, feel free to contact us at {settings.DEFAULT_FROM_EMAIL}.

Thank you for your order!

Sincerely,
Guerrier Clothing Team
    """
    send_mail(subject, text_message, settings.DEFAULT_FROM_EMAIL, [cust_email])

def convert_country(country_value):
    COUNTRY_MAP = {
        "Ireland": "IE",
        "United States": "US",
        "United Kingdom": "GB",
    }
    if len(country_value) == 2:
        return country_value.upper()
    return COUNTRY_MAP.get(country_value, country_value)
