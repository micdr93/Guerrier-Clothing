from django.urls import path
from . import views

app_name = "profiles" 

urlpatterns = [
    path('', views.profile_home, name='home'),
    path('edit/', views.profile_edit, name='edit'),
]