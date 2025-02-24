from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from products.models import Product

class SuggestedItem(models.Model):
    """
    Model to represent suggested/recommended products.
    """
    SUGGESTION_TYPES = [
        ('SIMILAR', 'Similar Products'),
        ('COMPLEMENTARY', 'Frequently Bought Together'),
        ('UPSELL', 'Premium Alternative'),
        ('TRENDING', 'Trending Now')
    ]
    
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE, 
        related_name='suggestions'
    )
    suggested_product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE, 
        related_name='suggested_for'
    )
    suggestion_type = models.CharField(
        max_length=50, 
        choices=SUGGESTION_TYPES
    )
    weight = models.FloatField(
        default=1.0, 
        validators=[
            MinValueValidator(0.0, "Weight cannot be negative"),
            MaxValueValidator(10.0, "Weight cannot exceed 10")
        ]
    )
    is_active = models.BooleanField(default=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["product", "suggested_product"], 
                name="unique_product_suggestion"
            )
        ]
        indexes = [
            models.Index(fields=['product', 'suggestion_type', '-weight']),
        ]
        verbose_name_plural = "Suggested Items"
    
    def __str__(self):
        return f"{self.get_suggestion_type_display()}: {self.product.name} → {self.suggested_product.name}"
    
    def clean(self):
        from django.core.exceptions import ValidationError
        
        # Prevent a product from suggesting itself
        if self.product == self.suggested_product:
            raise ValidationError("A product cannot suggest itself.")