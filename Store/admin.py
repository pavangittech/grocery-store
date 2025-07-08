from django.contrib import admin
from .models import Product, Order, orderitem, Payment
from .models import Wishlist

# Register your models here.

admin.site.register(Wishlist)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'stock')
    search_fields = ('name',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'total_amount', 'status', 'created_at']
    list_filter = ['status']
    search_fields = ['user__username', 'id']


@admin.register(orderitem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity')


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'order', 'status', 'transaction_id', 'created_at')  # ✅ Correct field name

