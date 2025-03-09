from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from home import views as home_views
from allauth.account.views import LogoutView
from products.sitemaps import StaticViewSitemap, ProductSitemap, CategorySitemap

sitemaps = {
    'static': StaticViewSitemap,
    'products': ProductSitemap,
    'categories': CategorySitemap,
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('', home_views.index, name='index'),
    path('', include('home.urls')),
    path('products/', include(('products.urls', 'products'), namespace='products')),
    path('clothing/', include(('products.urls', 'products'), namespace='clothing')),
    path('bag/', include(('bag.urls', 'bag'), namespace='bag')),
    path('checkout/', include(('checkout.urls', 'checkout'), namespace='checkout')),
    path('profiles/', include(('profiles.urls', 'profiles'), namespace='profiles')),
    path('wishlist/', include(('wishlist.urls', 'wishlist'), namespace='wishlist')),
    path('reviews/', include(('reviews.urls', 'reviews'), namespace='reviews')),
    path('recommendations/', include(('recommendations.urls', 'recommendations'), namespace='recommendations')),
    path("contact/", home_views.contact, name="contact"),
    path('shirts/', home_views.shirts_view, name='shirts'),
    path('hats/', home_views.hats_view, name='hats'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='sitemap')
]


if settings.DEBUG:
    print("serving media from:", settings.MEDIA_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
