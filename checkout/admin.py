from django.contrib import admin
from .models import Order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "order_number", "full_name", "order_total", "date")
    list_filter = ("date",)
    search_fields = ("order_number", "full_name", "email")
