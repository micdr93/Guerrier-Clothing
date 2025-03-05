from django import template

register = template.Library()

@register.filter(name='get_item')
def get_item(dictionary, key):
    """
    Filter to get an item from a dictionary using a key.
    Used to retrieve products from the all_products dictionary.
    """
    return dictionary.get(key)