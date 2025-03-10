from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('contact/', views.contact, name='contact'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('returns/', views.returns, name='returns'),
    path('shirts/', views.shirts_view, name='shirts_view'),
    path('hats/', views.hats_view, name='hats_view'),
    path('mugs/', views.mugs_view, name='mugs_view'),
    path('coasters/', views.coasters_view, name='coasters_view'),
    path('skateboard-decks/', views.skateboard_decks_view, name='skateboard_decks_view'),
]