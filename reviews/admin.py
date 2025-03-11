from django.contrib import admin
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "product",
        "user",
        "rating",
        "verified_purchase",
        "created_on",
    )
    list_filter = ("rating", "verified_purchase", "created_on")
    search_fields = ("title", "product__name", "user__username", "review")
    readonly_fields = ("created_on", "updated_on", "helpful_votes")
    ordering = ("-created_on",)

    fieldsets = (
        (
            "Review Information",
            {"fields": ("product", "user", "title", "review", "rating")},
        ),
        ("Status", {"fields": ("verified_purchase", "helpful_votes")}),
        ("Timestamps", {"fields": ("created_on", "updated_on")}),
    )
