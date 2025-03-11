from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from products.models import Product


class SuggestedItem(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="suggested_items"
    )
    suggestion_type = models.CharField(
        max_length=50,
        choices=[
            ("SIMILAR", "Similar Products"),
            ("COMPLEMENTARY", "Frequently Bought Together"),
            ("UPSELL", "Premium Alternative"),
            ("TRENDING", "Trending Now"),
        ],
    )
    weight = models.FloatField(
        default=1.0, validators=[MinValueValidator(0.0), MaxValueValidator(10.0)]
    )
    is_active = models.BooleanField(default=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["product", "suggestion_type", "-weight"]),
        ]
        verbose_name_plural = "Suggested Items"

    def __str__(self):
        return f"{self.get_suggestion_type_display()}: {self.product.name}"
