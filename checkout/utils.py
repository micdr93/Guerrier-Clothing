from django.core.mail import send_mail
from django.conf import settings

def send_confirmation_email(order):
    """Send the user a confirmation email"""
    cust_email = order.email
    subject = f'Guerrier Clothing - Order Confirmation {order.order_number}'
    
    # Create a plain text email body
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
    
    # Send email
    send_mail(
        subject,
        text_message,
        settings.DEFAULT_FROM_EMAIL,
        [cust_email],
    )