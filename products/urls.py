from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.all_products, name='products'),
    path('search/', views.search_results, name='search_results'),
    path('<int:product_id>/', views.product_detail, name='product_detail'),
    path('add/', views.add_product, name='add_product'),
    path('edit/<int:product_id>/', views.edit_product, name='edit_product'),
    path('delete/<int:product_id>/', views.delete_product, name='delete_product'),
    path('mugs/', views.mugs_view, name='mugs_view'),
    path('coasters/', views.coasters_view, name='coasters_view'),
    path('skateboard-decks/', views.skateboard_decks_view, name='skateboard_decks_view'),
]
