from django.contrib import admin
from django.urls import path, include
from home import views as home_views
from home.views import instant_logout, all_products
from django.conf import settings
from django.conf.urls.static import static

handler404 = 'guerrier_clothing.views.handler404'
handler500 = 'guerrier_clothing.views.handler500'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    
    # Home
    path('', home_views.index, name='index'),
    path('', include('home.urls')),  # if you have additional home app URLs
    path('products/', all_products, name='all_products'),
    
    # Products (and "clothing" if needed)
    path('products/', include(('products.urls', 'products'), namespace='products')),
    path('clothing/', include(('products.urls', 'products'), namespace='clothing')),  # if you want a separate namespace
    
    # Bag / Cart
    path('bag/', include(('bag.urls', 'bag'), namespace='bag')),
    
    # Checkout
    path('checkout/', include(('checkout.urls', 'checkout'), namespace='checkout')),
    
    # Profiles
    path('profiles/', include(('profiles.urls', 'profiles'), namespace='profiles')),
    
    # Wishlist
    path('wishlist/', include(('wishlist.urls', 'wishlist'), namespace='wishlist')),
    
    # Reviews
    path('reviews/', include(('reviews.urls', 'reviews'), namespace='reviews')),
    
    # Recommendations
    path('recommendations/', include(('recommendations.urls', 'recommendations'), namespace='recommendations')),
    
    # Contact and extra views from home
    path("contact/", home_views.contact, name="contact"),
    path('shirts/', home_views.shirts_view, name='shirts'),
    path('hats/', home_views.hats_view, name='hats'),
    
    # Logout (using your custom view)
    path('logout/', instant_logout, name='logout'),
]

# Add this as a separate statement
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)