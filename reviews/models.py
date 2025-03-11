from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User
from products.models import Product


class Review(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="reviews"
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="product_reviews"
    )

    title = models.CharField(max_length=100)
    review = models.TextField(max_length=1500)

    rating = models.IntegerField(
        validators=[
            MinValueValidator(1, "Rating must be at least 1"),
            MaxValueValidator(5, "Rating cannot exceed 5"),
        ]
    )

    verified_purchase = models.BooleanField(default=False)
    helpful_votes = models.PositiveIntegerField(default=0)

    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "product"], name="unique_review_per_user_new"
            )
        ]
        ordering = ["-created_on"]
        verbose_name_plural = "Reviews"

    def __str__(self):
        return f"{self.title} - {self.product.name}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.product.save()
