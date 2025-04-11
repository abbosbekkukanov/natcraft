# chat/serializers.py
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
    profile = UserProfileSerializer(read_only=True, required=False, allow_null=True)

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
        fields = ['id', 'message', 'user', 'reaction', 'created_at']
        read_only_fields = ['user', 'created_at']

    def validate_reaction(self, value):
        if not value:
            raise serializers.ValidationError("Reaction field cannot be empty.")
        return value

class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    images = MessageImageSerializer(many=True, read_only=True)
    voice = serializers.FileField(required=False)
    reply_to = serializers.PrimaryKeyRelatedField(queryset=Message.objects.all(), required=False)
    reactions = ReactionSerializer(many=True, read_only=True)
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), required=False)

    class Meta:
        model = Message
        fields = ['id', 'chat', 'sender', 'content', 'product', 'images', 'voice', 'reply_to', 'reactions', 'created_at', 'updated_at', 'is_read', 'is_edited']
        read_only_fields = ['chat', 'sender', 'created_at', 'updated_at', 'is_read']

    def validate(self, data):
        chat = self.context.get('chat')
        # API uchun request.user, WebSocket uchun sender ishlatiladi
        user = None
        if self.context.get('request'):
            user = self.context['request'].user
        elif self.context.get('sender'):
            user = self.context['sender']

        if not user:
            raise serializers.ValidationError("Foydalanuvchi aniqlanmadi")

        # Xabar bo‘sh emasligini tekshirish
        images = None
        if self.context.get('request'):
            images = self.context['request'].FILES.getlist('images')
        if not data.get('content') and not images and not data.get('voice'):
            raise serializers.ValidationError("Xabar bo'sh bo'lishi mumkin emas")

        # Chat ishtirokchisini tekshirish
        if chat and user not in [chat.seller, chat.buyer]:
            raise serializers.ValidationError("Siz bu chatda xabar yubora olmaysiz")

        return data

    def create(self, validated_data):
        # API uchun
        if self.context.get('request'):
            request = self.context.get('request')
            validated_data['sender'] = request.user
            images_data = request.FILES.getlist('images')
            message = Message.objects.create(**validated_data)
            for image_data in images_data:
                MessageImage.objects.create(message=message, image=image_data)
            return message
        # WebSocket uchun
        elif self.context.get('sender') and self.context.get('chat'):
            validated_data['sender'] = self.context['sender']
            validated_data['chat'] = self.context['chat']  # O‘ZGARISH: chat qo‘shildi
            message = Message.objects.create(**validated_data)
            return message
        raise serializers.ValidationError("Foydalanuvchi yoki chat aniqlanmadi")

    def update(self, instance, validated_data):
        images_data = self.context.get('request', {}).FILES.getlist('images') if self.context.get('request') else []
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