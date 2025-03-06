from django.urls import path
from . import views

app_name = 'bag'

urlpatterns = [
    path('', views.view_bag, name='view_bag'),
    path('add/<int:product_id>/', views.add_to_bag, name='add_to_bag'),
    path('update/<int:product_id>/', views.update_bag, name='update_bag'),
    path('remove/<int:product_id>/', views.remove_from_bag, name='remove_from_bag'),
]