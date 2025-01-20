from django.db import models
from products.models import Product
from django.contrib.auth.models import User


# Define the Wishlist model with specified fields
class Wishlist(models.Model):

    products = models.ManyToManyField(Product, blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True)  # noqa
    date_added = models.DateField(auto_now_add=True, blank=False, null=False)

    def __str__(self):
        return f"{self.user.username}'s Wishlist"