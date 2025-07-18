from django.urls import path
from . import views
from . import webhooks

app_name = "checkout"

urlpatterns = [
    path("", views.checkout, name="checkout"),
    path("checkout_success/<order_number>/", views.checkout_success, name="checkout_success"),
    path("cache_checkout_data/", views.cache_checkout_data, name="cache_checkout_data"),
    path("wh/", webhooks.webhook, name="webhook"),
    path("order/<order_number>/", views.order_detail, name="order_detail")
]
