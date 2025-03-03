from rest_framework import serializers
from .models import Product, Category, ProductImage, CartItem, Favorite, Comment, ViewedProduct


class CategorySerializer(serializers.ModelSerializer):
    # products = ProductSerializer(many=True, read_only=True)
    product_count = serializers.IntegerField(source='products.count', read_only=True)git
    class Meta:
        model = Category
        fields = "__all__"

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = "__all__"

class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    product_images = ProductImageSerializer(many=True, read_only=True)
    images = serializers.ListField(
        child=serializers.ImageField(), write_only=True, required=False
    )

    class Meta:
        model = Product
        fields = "__all__"
        read_only_fields = ['created_at', 'updated_at']

    def create(self, validated_data):
        images_data = self.context.get('request').FILES
        product = Product.objects.create(**validated_data)
        for image_data in images_data.getlist('images'):
            ProductImage.objects.create(product=product, image=image_data)
        return product


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = "__all__"
        

class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['id', 'user', 'product', 'quantity', 'added_at']


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'user', 'product', 'content', 'image', 'rating', 'created_at', 'updated_at']
        read_only_fields = ['user', 'created_at']

    def validate_rating(self, value):
        if not (1 <= value <= 5):
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value

    def create(self, validated_data):
        request = self.context.get("request")
        user = request.user
        comment = Comment.objects.create(user=user, **validated_data)
        return comment
    

# 19.11.2024
class ViewedProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = ViewedProduct
        fields = ['id', 'user', 'product', 'viewed_at']
        read_only_fields = ['user', 'viewed_at']