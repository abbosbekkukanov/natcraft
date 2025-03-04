from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.utils import timezone
# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(default='No description provided')
    image = models.ImageField(upload_to='category_images/', null=True, blank=True)


    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    threed_model = models.FileField(upload_to='3d_models/', null=True, blank=True)
    discount = models.DecimalField(max_digits=5, decimal_places=2,  null=True, blank=True, help_text="Discount in percent")
    address = models.CharField(max_length=255)
    view_count = models.PositiveIntegerField(default=0) 
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def upload_to(instance, filename):
        return 'product_images/{filename}'.format(filename=filename)

    def __str__(self):
        return self.name

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_images')
    image = models.ImageField(upload_to='product_images/')

    def __str__(self):
        return f"Image for {self.id}"
    

class Favorite(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='favorites')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'product')  # Har bir foydalanuvchi mahsulotni faqat bir marta yoqdirishi mumkin

    def __str__(self):
        return f"{self.user.username} likes {self.product.name}"
    

class CartItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cart_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='in_cart')
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')  # Har bir mahsulot foydalanuvchi savatchasida faqat bir marta bo'lishi kerak

    def __str__(self):
        return f"{self.quantity} of {self.product.name} in {self.user.username}'s cart"




class Comment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    image = models.ImageField(upload_to='comment_images/', null=True, blank=True)
    rating = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.product.name}"


# 19.11.2024

class ViewedProduct(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='viewed_products')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='viewed_by')
    viewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-viewed_at']  # Eng oxirgi ko‘rilgan mahsulotlarni tartibda ko'rsatadi

    def __str__(self):
        return f"{self.user.username} viewed {self.product.name}"