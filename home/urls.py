from django.urls import path
from products.views import all_products
from .views import mugs_view, coasters_view, skateboard_decks_view
from . import views


urlpatterns = [
    path('', views.index, name='home'),
    path('shirts/', views.shirts_view, name='shirts_view'),
    path('hats/', views.hats_view, name='hats_view'),
    path('homeware/mugs/', mugs_view, name='mugs_view'),
    path('homeware/coasters/', coasters_view, name='coasters_view'),
    path('homeware/skateboard-decks/', skateboard_decks_view, name='skateboard_decks_view'),
    path('contact/', views.contact, name='contact'),
    path('privacy_policy/', views.privacy_policy, name='privacy_policy'),
    path('returns/', views.returns, name='returns'),
   path('products/', all_products, name='products'),
]
