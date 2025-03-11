from django import forms
from django.core.validators import MinValueValidator, MaxValueValidator
from .widgets import CustomClearableFileInput
from .models import Product, Category
from reviews.models import Review  # Only needed if you do something with reviews here


class ProductForm(forms.ModelForm):
    """
    A form for creating/updating Product instances, including a custom
    clearable file widget for the optional image field.
    """

    # Custom field for image with specialized widget
    image = forms.ImageField(
        label="Image",
        required=False,
        widget=CustomClearableFileInput,
        help_text="Upload a product image (optional)",
    )

    # Additional validation for price
    price = forms.DecimalField(
        label="Price",
        min_value=0.01,
        max_value=10000,
        decimal_places=2,
        validators=[
            MinValueValidator(0.01, "Price must be greater than zero"),
            MaxValueValidator(10000, "Price is too high"),
        ],
        error_messages={
            "min_value": "Price must be a positive number",
            "max_value": "Price cannot exceed €10,000",
            "invalid": "Enter a valid price",
        },
    )

    # Additional validation for name
    name = forms.CharField(
        label="Product Name",
        max_length=254,
        min_length=3,
        error_messages={
            "min_length": "Product name must be at least 3 characters long",
            "max_length": "Product name cannot exceed 254 characters",
        },
    )

    # Optional rating field validation
    rating = forms.IntegerField(
        label="Rating",
        required=False,
        validators=[
            MinValueValidator(0, "Rating cannot be less than 0"),
            MaxValueValidator(5, "Rating cannot exceed 5"),
        ],
        error_messages={
            "invalid": "Enter a valid integer rating",
        },
        help_text="Optional rating from 0 to 5",
    )

    class Meta:
        model = Product
        fields = [
            "category",
            "sizes",
            "sku",
            "name",
            "description",
            "price",
            "rating",
            "image",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Populate category choices with friendly names
        categories = Category.objects.all()
        friendly_names = [(c.id, c.get_friendly_name() or c.name) for c in categories]
        self.fields["category"].choices = friendly_names

        # Add bootstrap-like styling to all fields
        for field_name, field in self.fields.items():
            if hasattr(field.widget, "attrs"):
                field.widget.attrs["class"] = "border-black rounded-0 form-control"

        # Make certain fields more user-friendly
        self.fields["description"].widget.attrs["rows"] = 3
        self.fields["sizes"].widget.attrs["class"] += " select2"

    def clean(self):
        """
        Additional form-level validation
        """
        cleaned_data = super().clean()
        name = cleaned_data.get("name")
        price = cleaned_data.get("price")

        # Prevent obviously problematic product entries
        if name and price:
            if len(name) < 3:
                self.add_error("name", "Product name is too short")

            if price <= 0:
                self.add_error("price", "Price must be greater than zero")

        return cleaned_data
