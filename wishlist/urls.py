
from django.urls import path
from . import views

urlpatterns = [
    path('', views.wishlist_home, name='wishlist_home'),
]