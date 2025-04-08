from rest_framework import serializers
from .models import Chat, Message, MessageImage, Reaction
from products.serializers import ProductSerializer
from products.models import Product
from accounts.models import CustomUser, UserProfile

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['profile_image', 'bio', 'phone_number', 'address']

class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'first_name', 'profile']

class MessageImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessageImage
        fields = ['id', 'image']

class ReactionSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Reaction
        fields = ['id', 'user', 'reaction', 'created_at']
        read_only_fields = ['user', 'created_at']

class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    images = MessageImageSerializer(many=True, read_only=True)
    voice = serializers.FileField(required=False)
    reply_to = serializers.PrimaryKeyRelatedField(queryset=Message.objects.all(), required=False)
    reactions = ReactionSerializer(many=True, read_only=True)
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), required=False)

    class Meta:
        model = Message
        fields = ['id', 'chat', 'sender', 'content', 'product', 'images', 'voice', 'reply_to', 'reactions', 'created_at', 'updated_at', 'is_read']
        read_only_fields = ['chat', 'sender', 'created_at', 'updated_at', 'is_read']

    def validate(self, data):
        request = self.context.get('request')
        chat = self.context.get('chat')

        if not data.get('content') and not self.context['request'].FILES.getlist('images') and not data.get('voice'):
            raise serializers.ValidationError("Xabar bo'sh bo'lishi mumkin emas")

        if chat and request.user not in [chat.seller, chat.buyer]:
            raise serializers.ValidationError("Siz bu chatda xabar yubora olmaysiz")

        return data

    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['sender'] = request.user
        images_data = request.FILES.getlist('images')
        message = Message.objects.create(**validated_data)
        for image_data in images_data:
            MessageImage.objects.create(message=message, image=image_data)
        return message

    def update(self, instance, validated_data):
        images_data = self.context.get('request').FILES.getlist('images')
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.is_edited = True
        instance.save()
        if images_data:
            for image_data in images_data:
                MessageImage.objects.create(message=instance, image=image_data)
        return instance

class ChatSerializer(serializers.ModelSerializer):
    seller = UserSerializer(read_only=True)
    buyer = UserSerializer(read_only=True)
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), required=False)
    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = Chat
        fields = ['id', 'product', 'seller', 'buyer', 'created_at', 'updated_at', 'messages']
        read_only_fields = ['seller', 'buyer', 'created_at', 'updated_at']

    def create(self, validated_data):
        request = self.context.get('request')
        product = validated_data.get('product', None)
        
        if product:
            seller = product.user
        else:
            raise serializers.ValidationError("Chat boshlash uchun mahsulot ID’si talab qilinadi")

        return Chat.objects.create(
            product=product,
            seller=seller,
            buyer=request.user,
        )