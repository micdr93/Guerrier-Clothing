from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from decimal import Decimal


class Category(models.Model):
    class Meta:
        verbose_name_plural = "Categories"

    name = models.CharField(max_length=254, unique=True)
    friendly_name = models.CharField(max_length=254, null=True, blank=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    def get_friendly_name(self):
        return self.friendly_name


class Size(models.Model):
    SIZE_CHOICES = [
        ("S", "Small"),
        ("M", "Medium"),
        ("L", "Large"),
        ("XL", "Extra Large"),
        ("XXL", "2X Large"),
    ]

    name = models.CharField(max_length=3, choices=SIZE_CHOICES, unique=True)

    def __str__(self):
        return self.get_name_display()


class Product(models.Model):
    # Removed redundant "updated" field; use created_at and updated_at below.
    category = models.ForeignKey(
        Category,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="products",
    )
    sizes = models.ManyToManyField(Size, blank=True, related_name="products")

    sku = models.CharField(max_length=254, null=True, blank=True, unique=True)
    name = models.CharField(max_length=254)
    description = models.TextField(max_length=1000, default="Default description")

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal("0.01"), "Price must be greater than zero"),
            MaxValueValidator(Decimal("99999.99"), "Price is too high"),
        ],
    )

    rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[
            MinValueValidator(0, "Rating cannot be negative"),
            MaxValueValidator(5, "Rating cannot exceed 5"),
        ],
    )
    image = models.ImageField(null=True, blank=True, upload_to="product_images/")

    color = models.CharField(max_length=20, blank=True, null=True)
    gender = models.CharField(max_length=1, default="U")

    is_active = models.BooleanField(default=True)
    is_new = models.BooleanField(default=False)
    on_sale = models.BooleanField(default=False)
    discount_percent = models.IntegerField(default=0)
    featured = models.BooleanField(default=False)
    in_stock = models.BooleanField(default=True)
    stock_qty = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def update_rating(self):
        from django.db.models import Avg

        reviews = self.reviews.all()
        if reviews.exists():
            self.rating = round(reviews.aggregate(Avg("rating"))["rating__avg"], 1)
        else:
            self.rating = 0
        self.save(update_fields=["rating"])

    def __str__(self):
        return self.name

    def soft_delete(self):
        self.is_active = False
        self.deleted_at = timezone.now()
        self.save()

    def restore(self):
        self.is_active = True
        self.deleted_at = None
        self.save()
        
    def get_available_sizes(self):
        return list(self.sizes.all())

    @classmethod
    def active_products(cls):
        return cls.objects.filter(is_active=True)

    def format_price(self):
        return f"€{self.price:.2f}"

    def get_discount_price(self):
        if self.on_sale and self.discount_percent > 0:
            discount = self.price * (Decimal(self.discount_percent) / 100)
            return self.price - discount
        return self.price
