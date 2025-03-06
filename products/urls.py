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
    path('add_review/<int:product_id>/', views.add_review, name='add_review'),
    path('update_review/<int:pk>/', views.UpdateReview.as_view(), name='update_review'),
    path('delete_review/<int:pk>/', views.DeleteReview.as_view(), name='delete_review'),
]
