from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('summernote/', include('django_summernote.urls')),
    path("privacy_policy", views.privacy_policy, name="privacy_policy"),
    path("returns", views.returns, name="returns"),
    path("contact", views.contact, name="contact"),
]