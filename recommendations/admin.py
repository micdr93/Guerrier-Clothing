from django.contrib import admin
from .models import SuggestedItem

@admin.register(SuggestedItem)
class SuggestedItemAdmin(admin.ModelAdmin):
    list_display = ('product', 'suggested_product', 'suggestion_type', 'weight', 'is_active')
    list_filter = ('suggestion_type', 'is_active', 'created_on')
    search_fields = ('product__name', 'suggested_product__name')
    readonly_fields = ('created_on', 'updated_on')
    
    fieldsets = (
        ('Suggestion Information', {
            'fields': ('product', 'suggested_product', 'suggestion_type', 'weight', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_on', 'updated_on')
        }),
    )