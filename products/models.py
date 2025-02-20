from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

class Category(models.Model):
    """
    Model to represent product categories.
    """
    class Meta:
        verbose_name_plural = 'Categories'

    name = models.CharField(max_length=254, unique=True)
    friendly_name = models.CharField(max_length=254, null=True, blank=True)
    description = models.TextField(blank=True, null=True)

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
    Enhanced Product model with additional features and validations.
    """
    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.SET_NULL, related_name='products')
    sizes = models.ManyToManyField(Size, blank=True, related_name='products')
    
    sku = models.CharField(max_length=254, null=True, blank=True, unique=True)
    name = models.CharField(max_length=254)
    description = models.TextField(max_length=1000, default="Default description")
    
    price = models.DecimalField(
        max_digits=6, 
        decimal_places=2, 
        validators=[
            MinValueValidator(0.01, "Price must be greater than zero"),
            MaxValueValidator(10000, "Price is too high")
        ]
    )
    
    rating = models.DecimalField(
        max_digits=3, 
        decimal_places=2, 
        null=True, 
        blank=True,
        validators=[
            MinValueValidator(0, "Rating cannot be negative"),
            MaxValueValidator(5, "Rating cannot exceed 5")
        ]
    )
    
    image_url = models.URLField(max_length=1024, null=True, blank=True)
    image = models.ImageField(null=True, blank=True, upload_to='product_images/')
    
    # Soft delete fields
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name

    def soft_delete(self):
        """
        Soft delete the product instead of hard deleting
        """
        self.is_active = False
        self.deleted_at = timezone.now()
        self.save()

    def restore(self):
        """
        Restore a soft-deleted product
        """
        self.is_active = True
        self.deleted_at = None
        self.save()

    def get_available_sizes(self):
        """
        Return list of available sizes for this product
        """
        return list(self.sizes.all())

    @classmethod
    def active_products(cls):
        """
        Returns only active products
        """
        return cls.objects.filter(is_active=True)

class Review(models.Model):
    """
    Model to represent product reviews with enhanced features.
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='product_reviews')
    
    title = models.CharField(max_length=100)
    review = models.TextField(max_length=1500)
    
    rating = models.IntegerField(
        validators=[
            MinValueValidator(1, "Rating must be at least 1"),
            MaxValueValidator(5, "Rating cannot exceed 5")
        ]
    )
    
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "product"], 
                name="unique_review_per_user"
            )
        ]
        ordering = ['-created_on']
        verbose_name_plural = "Reviews"

    def __str__(self):
        return f"{self.title} - {self.product.name}"