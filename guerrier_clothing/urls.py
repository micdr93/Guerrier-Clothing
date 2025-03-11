from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from django.urls import re_path
from django.views.static import serve  # Import Django's built-in serve function
from products.sitemaps import StaticViewSitemap, ProductSitemap, CategorySitemap
from products import views as product_views

sitemaps = {
    "static": StaticViewSitemap,
    "products": ProductSitemap,
    "categories": CategorySitemap,
}

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path("", include(("home.urls", "home"), namespace="home")),
    path("products/", include(("products.urls", "products"), namespace="products")),
    path("clothing/", include(("products.urls", "products"), namespace="clothing")),
    path("bag/", include(("bag.urls", "bag"), namespace="bag")),
    path("checkout/", include(("checkout.urls", "checkout"), namespace="checkout")),
    path("profiles/", include(("profiles.urls", "profiles"), namespace="profiles")),
    path("wishlist/", include(("wishlist.urls", "wishlist"), namespace="wishlist")),
    path("reviews/", include(("reviews.urls", "reviews"), namespace="reviews")),
    path(
        "recommendations/",
        include(
            ("recommendations.urls", "recommendations"), namespace="recommendations"
        ),
    ),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="sitemap"),
    path("homeware/mugs/", product_views.mugs_view, name="homeware_mugs"),
    path("homeware/coasters/", product_views.coasters_view, name="homeware_coasters"),
    path(
        "homeware/skateboard-decks/",
        product_views.skateboard_decks_view,
        name="homeware_skateboard_decks",
    ),
]

# Always serve media files regardless of DEBUG setting
urlpatterns += [
    re_path(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}),
]

# Only serve static files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
