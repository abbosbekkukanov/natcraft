from django.contrib import admin
from .models import Category, Product, ProductImage, Favorite, CartItem, Comment

# ProductImage modelini Product ichida inline sifatida ko'rsatish uchun
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1  # Qo'shimcha rasm maydonini ko'rsatish uchun

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'category', 'address')
    search_fields = ('name', 'description', 'address')
    list_filter = ('category',)
    inlines = [ProductImageInline] 

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'image')
    search_fields = ('name', 'description')

@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('product', 'image')

@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'created_at')
    search_fields = ('user__username', 'product__name')

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'quantity', 'added_at')
    search_fields = ('user__username', 'product__name') 

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'created_at', 'content')
    search_fields = ('user__username', 'product__name', 'content')
