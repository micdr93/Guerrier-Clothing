from products.models import Product
from django.db.models import Q

def get_recommended_items(user_products, limit=4):
    """
    Returns a queryset of recommended products based on the categories of the given products.
    Excludes products that are already in the user's bag or wishlist.
    
    Accepts either a queryset or a list of Product instances.
    """
    if not user_products:
        return Product.objects.none()
    
    # Determine if user_products is a queryset or a list
    if hasattr(user_products, 'values_list'):
        # It's a queryset; use the ORM methods directly
        categories = user_products.values_list('category', flat=True).distinct()
        product_ids = user_products.values_list('id', flat=True)
    else:
        # It's a list; use list comprehensions
        categories = list(set([p.category for p in user_products]))
        product_ids = [p.id for p in user_products]
    
    recommendations = Product.objects.filter(category__in=categories).exclude(id__in=product_ids).distinct()[:limit]
    return recommendations
