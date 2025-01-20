
from django.contrib import admin
from django.urls import path, include
from home import views  
from django.conf import settings
from django.conf.urls.static import static
from home import views as home_views

handler404 = 'guerrier_clothing.views.handler404'
handler500 = 'guerrier_clothing.views.handler500'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('', include('home.urls')), 
    path('products/', include('products.urls')),
    path('bag/', include('bag.urls')),
    path('checkout/', include('checkout.urls')),
    path('profiles/', include('profiles.urls')),
    path('wishlist/', include('wishlist.urls')),
    path("contact/", views.contact, name="contact"),
    path('shirts/', views.shirts_view, name='shirts'),
    path('hats/', views.hats_view, name='hats'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
