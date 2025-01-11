
from django.contrib import admin
from django.urls import path, include
from home import views  
from django.conf import settings
from django.conf.urls.static import static

handler404 = 'guerrier_clothing.views.handler404'
handler500 = 'guerrier_clothing.views.handler500'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('', include('home.urls')),  # Home page handled by 'home.urls'
    path('products/', include('products.urls')),
    path('bag/', include('bag.urls')),
    path('checkout/', include('checkout.urls')),
    path('profiles/', include('profiles.urls')),
    path('wishlist/', include('wishlist.urls')),
    path('contact/', views.contact, name='contact'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
