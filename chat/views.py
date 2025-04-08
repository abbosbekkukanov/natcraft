from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Chat, Message, Reaction
from .serializers import ChatSerializer, MessageSerializer, ReactionSerializer
from products.models import Product
from django.shortcuts import get_object_or_404
from django.db import models
from .permissions import IsChatParticipant


class ChatViewSet(viewsets.ModelViewSet):
    serializer_class = ChatSerializer
    permission_classes = [permissions.IsAuthenticated, IsChatParticipant]

    def get_queryset(self):
        """Faqat foydalanuvchi ishtirok etgan chatlarni qaytaradi"""
        user = self.request.user
        return Chat.objects.filter(models.Q(seller=user) | models.Q(buyer=user))

    def create(self, request, *args, **kwargs):
        """Yangi chat yaratish"""
        product_id = request.data.get('product')
        if not product_id:
            return Response({"error": "Mahsulot ID'si talab qilinadi"}, status=status.HTTP_400_BAD_REQUEST)
        
        product = get_object_or_404(Product, id=product_id)
        if product.user == request.user:
            return Response({"error": "O‘zingiz bilan chat boshlay olmaysiz"}, status=status.HTTP_400_BAD_REQUEST)
        
        existing_chat = Chat.objects.filter(product=product, seller=product.user, buyer=request.user).first()
        if existing_chat:
            serializer = self.get_serializer(existing_chat)
            return Response(serializer.data, status=status.HTTP_200_OK)

        # Serializerga context sifatida request uzatamiz
        serializer = self.get_serializer(data={'product': product.id}, context={'request': request})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        serializer.save(context={'request': self.request})

    @action(detail=True, methods=['get'], url_path='messages')
    def get_messages(self, request, pk=None):
        chat = self.get_object()
        messages = chat.messages.all()
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='send-message')
    def send_message(self, request, pk=None):
        chat = self.get_object()
        serializer = MessageSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(chat=chat)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], url_path='messages/(?P<message_id>\d+)/react')
    def add_reaction(self, request, pk=None, message_id=None):
        chat = self.get_object()
        message = get_object_or_404(Message, id=message_id, chat=chat)
        reaction_data = {'message': message.id, 'reaction': request.data.get('reaction')}
        serializer = ReactionSerializer(data=reaction_data, context={'request': request})
        if serializer.is_valid():
            existing_reaction = Reaction.objects.filter(message=message, user=request.user).first()
            if existing_reaction:
                existing_reaction.reaction = reaction_data['reaction']
                existing_reaction.save()
                return Response(ReactionSerializer(existing_reaction).data, status=status.HTTP_200_OK)
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['put'], url_path='messages/(?P<message_id>\d+)/edit')
    def edit_message(self, request, pk=None, message_id=None):
        chat = self.get_object()
        message = get_object_or_404(Message, id=message_id, chat=chat)
        if message.sender != request.user:
            return Response({"error": "Faqat o‘zingizning xabaringizni tahrirlashingiz mumkin"}, status=status.HTTP_403_FORBIDDEN)
        serializer = MessageSerializer(message, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['delete'], url_path='messages/(?P<message_id>\d+)/delete')
    def delete_message(self, request, pk=None, message_id=None):
        chat = self.get_object()
        message = get_object_or_404(Message, id=message_id, chat=chat)
        if message.sender != request.user:
            return Response({"error": "Faqat o‘zingizning xabaringizni o‘chirishingiz mumkin"}, status=status.HTTP_403_FORBIDDEN)
        message.delete()
        return Response({"status": "Xabar o‘chirildi"}, status=status.HTTP_204_NO_CONTENT)