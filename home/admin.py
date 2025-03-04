from django.contrib import admin
from .models import Product, Category
from .models import NewsletterSubscription

@admin.register(NewsletterSubscription)
class NewsletterSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('email', 'date_added')
    search_fields = ('email',)
    list_filter = ('date_added',)
    readonly_fields = ('date_added',)
    ordering = ('-date_added',)
    actions = ['export_emails']
    
    def export_emails(self, request, queryset):
        self.message_user(request, f"{queryset.count()} email addresses selected for export.")
    export_emails.short_description = "Export selected email addresses"

admin.site.register(Product)
admin.site.register(Category)