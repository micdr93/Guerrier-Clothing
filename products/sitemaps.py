from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Product

# 1. Static pages
class StaticViewSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.80

    def items(self):
        # These are the named URL patterns from your urls.py
        return [
            'index',             # /
            'account_signup',   # /accounts/signup/ (if you have a name for it)
            'account_login',    # /accounts/login/
            'bag:view_bag',    # /bag/
            'contact',           # /contact/
            'privacy_policy',    # /privacy_policy
            'returns',           # /returns
            # Add any others as needed
        ]

    def location(self, item):
        return reverse(item)

# 2. Product detail pages
class ProductSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.64

    def items(self):
        # Return all product objects
        return Product.objects.all()

    def lastmod(self, obj):
        # If your Product model has a field like 'updated_at'
        return obj.updated_at

    def location(self, obj):
        # Adjust if your URL uses a slug instead of ID
        return reverse('products:product_detail', kwargs={'product_id': obj.pk})


# 3. Filtered pages (by category, brand, etc.)
class FilterSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.80

    # Define all combinations you want in the sitemap
    # For dynamic generation, you might fetch from your database or define them manually
    filter_combinations = [
        # Example combos (similar to your XML):
        {'category': 'mens_trainers', 'gender': 'men'},
        {'category': 'mens_socks', 'gender': 'men'},
        {'category': 'mens_water_bottles', 'gender': 'men'},
        {'category': 'mens_sale'},
        {'category': 'womens_sale'},
        # brand combos, multiple categories, etc.
        # ...
    ]

    def items(self):
        return self.filter_combinations

    def location(self, item):
        """
        Build a URL with query parameters like /products/?category=xxx&gender=yyy
        Adjust as needed based on how your product list URL is named and structured.
        """
        base_url = reverse('products:product_list')  # e.g., path('products/', ...)
        query_parts = []
        if 'category' in item:
            query_parts.append(f'category={item["category"]}')
        if 'gender' in item:
            query_parts.append(f'gender={item["gender"]}')
        if query_parts:
            return f'{base_url}?{"&".join(query_parts)}'
        return base_url