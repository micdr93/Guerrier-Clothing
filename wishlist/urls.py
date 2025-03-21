from django.urls import path
from . import views

app_name = "wishlist"

urlpatterns = [
    path("", views.wishlist_home, name="wishlist_home"),
    path("add/<int:product_id>/", views.add_to_wishlist, name="add_to_wishlist"),
    path(
        "remove/<int:product_id>/",
        views.remove_from_wishlist,
        name="remove_from_wishlist",
    ),
]
