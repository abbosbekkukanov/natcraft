from rest_framework import serializers
from .models import Chat, Message, MessageImage, Reaction
from products.serializers import ProductSerializer, Product
from accounts.models import CustomUser, UserProfile

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['profile_image', 'bio', 'phone_number', 'address']

class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'first_name', 'last_name', 'profile']

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
    images = MessageImageSerializer(many=True, read_only=True)  # Ko‘p rasmlar
    voice = serializers.FileField(required=False)  # Ovozli xabar
    reply_to = serializers.PrimaryKeyRelatedField(queryset=Message.objects.all(), required=False)  # Javob xabari ID’si
    reactions = ReactionSerializer(many=True, read_only=True)  # Reaktsiyalar

    class Meta:
        model = Message
        fields = ['id', 'chat', 'sender', 'content', 'images', 'voice', 'reply_to', 'reactions', 'created_at', 'updated_at', 'is_read']
        read_only_fields = ['sender', 'created_at', 'updated_at', 'is_read']

    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['sender'] = request.user
        images_data = request.FILES.getlist('images')  # Ko‘p rasmlarni olish
        message = Message.objects.create(**validated_data)
        for image_data in images_data:
            MessageImage.objects.create(message=message, image=image_data)
        return message

    def update(self, validated_data):
        images_data = self.context.get('request').FILES.getlist('images')
        message = self.instance
        for attr, value in validated_data.items():
            setattr(message, attr, value)
        message.save()
        if images_data:
            # Eski rasmlarni o‘chirib, yangilarini qo‘shish mumkin yoki qo‘shib borish
            for image_data in images_data:
                MessageImage.objects.create(message=message, image=image_data)
        return message

class ChatSerializer(serializers.ModelSerializer):
    seller = UserSerializer(read_only=True)
    buyer = UserSerializer(read_only=True)
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())  # ID uchun
    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = Chat
        fields = ['id', 'product', 'seller', 'buyer', 'created_at', 'updated_at', 'messages']
        read_only_fields = ['seller', 'buyer', 'created_at', 'updated_at']  # buyer ham read_only

    def create(self, validated_data):
        request = self.context.get('request')
        print(f"validated_data: {validated_data}")
        product = validated_data['product'] 
        print(f"product: {product}")
        validated_data['seller'] = product.user
        validated_data['buyer'] = request.user
        return Chat.objects.create(**validated_data)