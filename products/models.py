from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    """
    Model to represent product categories.
    """
    class Meta:
        verbose_name_plural = 'Categories'

    name = models.CharField(max_length=254)
    friendly_name = models.CharField(max_length=254, null=True, blank=True)

    def __str__(self):
        return self.name

    def get_friendly_name(self):
        return self.friendly_name

class Size(models.Model):
    """
    Model to represent available sizes for products.
    """
    SIZE_CHOICES = [
        ('S', 'Small'),
        ('M', 'Medium'),
        ('L', 'Large'),
        ('XL', 'Extra Large'),
        ('XXL', '2X Large'),
    ]

    name = models.CharField(max_length=3, choices=SIZE_CHOICES, unique=True)

    def __str__(self):
        return self.get_name_display()

class Product(models.Model):
    """
    Model to represent products.
    """
    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.SET_NULL)
    sizes = models.ManyToManyField(Size, blank=True)
    sku = models.CharField(max_length=254, null=True, blank=True)
    name = models.CharField(max_length=254)
    description = models.CharField(max_length=255, default="Default description")
    price = models.DecimalField(max_digits=6, decimal_places=2)
    rating = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    image_url = models.URLField(max_length=1024, null=True, blank=True)
    image = models.ImageField(null=True, blank=True)

    def __str__(self):
        return self.name

class Review(models.Model):
    """
    Model to represent product reviews.
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100, blank=True)
    review = models.TextField(max_length=1500, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "product"], name="unique_review_per_user"
            )
        ]
        verbose_name_plural = "Reviews"

    def __str__(self):
        return self.title if self.title else f"Review for {self.product.name}"