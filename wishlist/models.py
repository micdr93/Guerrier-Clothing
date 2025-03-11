from django.db import models
from django.contrib.auth.models import User
from products.models import Product


class Wishlist(models.Model):
    """
    Model to represent user wishlists.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="wishlists")
    name = models.CharField(max_length=100, default="My Wishlist")
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    is_public = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "Wishlists"

    def __str__(self):
        return f"{self.name} - {self.user.username}"

    def get_item_count(self):
        """Return the number of items in the wishlist"""
        return self.items.count()


class WishlistItem(models.Model):
    """
    Model to represent individual items in a wishlist.
    """

    wishlist = models.ForeignKey(
        Wishlist, on_delete=models.CASCADE, related_name="items"
    )
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="in_wishlists"
    )
    added_on = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)

    PRIORITY_CHOICES = [(1, "Low"), (2, "Medium"), (3, "High")]

    priority = models.IntegerField(choices=PRIORITY_CHOICES, default=2)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["wishlist", "product"], name="unique_product_per_wishlist"
            )
        ]
        ordering = ["-priority", "-added_on"]
        verbose_name_plural = "Wishlist Items"

    def __str__(self):
        return f"{self.product.name} in {self.wishlist.name}"
