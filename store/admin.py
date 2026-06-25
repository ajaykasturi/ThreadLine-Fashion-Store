from django.contrib import admin
from .models import (Category, Product, ProductImage, UserProfile, Order, OrderItem,
                     Review, ContactMessage)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'brand', 'category', 'price', 'stock', 'sizes', 'uploaded_by')
    list_filter = ('brand', 'category')
    search_fields = ('name', 'description')
    inlines = [ProductImageInline]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'full_name', 'city', 'province', 'total', 'status', 'created_at')
    list_filter = ('status',)
    inlines = [OrderItemInline]


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'submitted_at', 'is_read')
    list_filter = ('is_read', 'submitted_at')
    search_fields = ('name', 'email', 'subject', 'message')
    readonly_fields = ('name', 'email', 'subject', 'message', 'submitted_at', 'user')
    list_editable = ('is_read',)


admin.site.register(Category)
admin.site.register(UserProfile)
admin.site.register(Review)
