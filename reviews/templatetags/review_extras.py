from django import template
from django.db.models import Avg

register = template.Library()

@register.simple_tag
def average_rating(product):
    result = product.reviews.aggregate(avg_rating=Avg("rating"))
    avg = result.get("avg_rating")
    return f"{avg:.1f}" if avg is not None else ""
