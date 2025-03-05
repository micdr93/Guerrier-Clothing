from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Product, Category

class StaticViewSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.80

    def items(self):
        return [
            'index',
            'account_signup',
            'account_login',
            'bag:view_bag',
            'contact',
            'privacy_policy',
            'returns',
        ]

    def location(self, item):
        return reverse(item)

class ProductSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.64

    def items(self):
        return Product.objects.all()

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return reverse('products:product_detail', kwargs={'product_id': obj.pk})

class CategorySitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return Category.objects.all().order_by('name')

    def location(self, obj):
        base_url = reverse('products:product_list')
        return f"{base_url}?category={obj.name.lower()}"
