from django.contrib import admin
from .models import Item, StripeInfo, Order, OrderItem, Tax, Discount


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ["name", "price"]


@admin.register(StripeInfo)
class ItemInfoAdmin(admin.ModelAdmin):
    list_display = ["item", "stripe_product_id", "stripe_price_id"]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    pass


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    pass


@admin.register(Tax)
class TaxAdmin(admin.ModelAdmin):
    list_display = ['name', 'amount', 'order']


@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = ['name', 'amount', 'order']
