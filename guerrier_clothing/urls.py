
from django.contrib import admin
from django.urls import path, include
from home import views  
from django.conf import settings
from django.conf.urls.static import static
from home import views as home_views
from home.views import instant_logout

handler404 = 'guerrier_clothing.views.handler404'
handler500 = 'guerrier_clothing.views.handler500'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('', views.index, name='index'),
    path('', include('home.urls')), 
    path('products/', include('products.urls')),
    path('bag/', include(('bag.urls', 'bag'), namespace='bag')),
    path('checkout/', include('checkout.urls')),
    path('profiles/', include('profiles.urls')),
    path('accounts/', include('allauth.urls')),
    path('logout/', instant_logout, name='logout'),
    path('clothing/', include('products.urls')),
    path('wishlist/', include('wishlist.urls')),
    path('reviews/', include('reviews.urls', namespace='product_reviews')),
    path('recommendations/', include('recommendations.urls')),
    path("contact/", views.contact, name="contact"),
    path('shirts/', views.shirts_view, name='shirts'),
    path('hats/', views.hats_view, name='hats'),
    path('webhooks/', include('checkout.urls', namespace='checkout')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
