from django.contrib import admin
from .models import Wishlist, WishlistItem


class WishlistItemInline(admin.TabularInline):
    model = WishlistItem
    extra = 1
    readonly_fields = ("added_on",)


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "get_item_count", "is_public", "created_on")
    list_filter = ("is_public", "created_on")
    search_fields = ("name", "user__username")
    readonly_fields = ("created_on", "updated_on")
    inlines = [WishlistItemInline]

    fieldsets = (
        ("Wishlist Information", {"fields": ("user", "name", "is_public")}),
        ("Timestamps", {"fields": ("created_on", "updated_on")}),
    )


@admin.register(WishlistItem)
class WishlistItemAdmin(admin.ModelAdmin):
    list_display = ("product", "wishlist", "priority", "added_on")
    list_filter = ("priority", "added_on")
    search_fields = ("product__name", "wishlist__name", "notes")
    readonly_fields = ("added_on",)

    fieldsets = (
        ("Item Information", {"fields": ("wishlist", "product", "priority", "notes")}),
        ("Timestamps", {"fields": ("added_on",)}),
    )
