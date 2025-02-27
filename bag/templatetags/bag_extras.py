
from django import template

register = template.Library()

@register.filter
def calc_subtotal(price, quantity):
    try:
        return price * int(quantity)
    except (ValueError, TypeError):
        return ''