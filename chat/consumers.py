import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Chat, Message, Reaction
from .serializers import MessageSerializer, ReactionSerializer
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
from products.models import Product

logger = logging.getLogger(__name__)

class ChatConsumer(AsyncWebsocketConsumer):
    async def create_chat(self, data):
        product_id = data.get('product')
        if not product_id:
            await self.send_error("product talab qilinadi")
            return

        product = await database_sync_to_async(get_object_or_404)(Product, id=product_id)
        seller = product.user
        buyer = self.scope['user']

        if seller == buyer:
            await self.send_error("O‘zingiz bilan chat boshlay olmaysiz")
            return

        chat, created = await database_sync_to_async(Chat.objects.get_or_create)(
            seller=seller, buyer=buyer, defaults={'product': product}
        )
        if created:
            await self.send(text_data=json.dumps({
                'action': 'chat_created',
                'chat_id': chat.id
            }))

    async def connect(self):
        self.chat_id = self.scope['url_route']['kwargs']['chat_id']
        self.chat_group_name = f'chat_{self.chat_id}'
        logger.info(f"WebSocket ulanish boshlandi: chat_id={self.chat_id}, user={self.scope['user'].email if not self.scope['user'].is_anonymous else 'anonymous'}")

        # Foydalanuvchi autentifikatsiya qilinganligini tekshirish
        if self.scope['user'].is_anonymous:
            logger.error(f"Anonim foydalanuvchi ulanishga urindi: chat_id={self.chat_id}")
            await self.close(code=4001)
            return

        # Foydalanuvchi chat ishtirokchisi ekanligini tekshirish
        if await self.is_chat_participant():
            logger.info(f"Chat ishtirokchisi tasdiqlandi: user={self.scope['user'].email}, chat_id={self.chat_id}")
            await self.channel_layer.group_add(
                self.chat_group_name,
                self.channel_name
            )
            await self.accept()
            logger.info(f"Ulanish muvaffaqiyatli: chat_id={self.chat_id}, channel_name={self.channel_name}")
        else:
            logger.error(f"Foydalanuvchi chat ishtirokchisi emas: user={self.scope['user'].email}, chat_id={self.chat_id}")
            await self.close(code=4003) 

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.chat_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            action = data.get('action')
            logger.info(f"Xabar qabul qilindi: chat_id={self.chat_id}, action={action}, data={data}")
            if not action:
                logger.error(f"Action yetishmayapti: chat_id={self.chat_id}")
                await self.send_error("Action talab qilinadi")
                return

            handlers = {
                'create_chat': self.create_chat,
                'send_message': self.send_message,
                'edit_message': self.edit_message,
                'delete_message': self.delete_message,
                'add_reaction': self.add_reaction,
                'remove_reaction': self.remove_reaction,
                'sync_message': self.sync_message,
            }

            handler = handlers.get(action)
            if handler:
                await handler(data)
            else:
                logger.error(f"Noto‘g‘ri action: chat_id={self.chat_id}, action={action}")
                await self.send_error("Noto‘g‘ri action")
        except json.JSONDecodeError as e:
            logger.error(f"JSON xatosi: chat_id={self.chat_id}, error={str(e)}, text_data={text_data}")
            await self.send_error("Xato JSON formati")

    # Yordamchi metodlar
    @database_sync_to_async
    def is_chat_participant(self):
        chat = get_object_or_404(Chat, id=self.chat_id)
        user = self.scope['user']
        return user == chat.seller or user == chat.buyer

    async def send_error(self, message):
        await self.send(text_data=json.dumps({'error': message}))

    # Xabar operatsiyalari
    async def send_message(self, data):
        content = data.get('content')
        product_id = data.get('product')
        if not content:
            await self.send_error("Xabar matni talab qilinadi")
            return

        chat = await database_sync_to_async(get_object_or_404)(Chat, id=self.chat_id)
        message_data = {'chat': chat.id, 'sender': self.scope['user'].id, 'content': content}
        if product_id:
            message_data['product'] = product_id

        serializer = MessageSerializer(data=message_data, context={'chat': chat, 'sender': self.scope['user']})
        if await database_sync_to_async(serializer.is_valid)():
            message = await database_sync_to_async(serializer.save)()
            await self.channel_layer.group_send(
                self.chat_group_name,
                {
                    'type': 'chat_message',
                    'action': 'new',
                    'message': MessageSerializer(message, context={'chat': chat}).data
                }
            )
        else:
            await self.send_error("Xabar yuborishda xato: noto‘g‘ri ma’lumotlar")

    async def sync_message(self, data):
        message_id = data.get('message_id')
        if not message_id:
            await self.send_error("message_id talab qilinadi")
            return

        message = await database_sync_to_async(get_object_or_404)(Message, id=message_id, chat_id=self.chat_id)
        chat = await database_sync_to_async(get_object_or_404)(Chat, id=self.chat_id)
        await self.channel_layer.group_send(
            self.chat_group_name,
            {
                'type': 'chat_message',
                'action': 'new',
                'message': MessageSerializer(message, context={'chat': chat}).data
            }
        )
        logger.info(f"Xabar sinxronlashtirildi: chat_id={self.chat_id}, message_id={message.id}")

    async def edit_message(self, data):
        message_id = data.get('message_id')
        content = data.get('content')
        if not message_id or not content:
            await self.send_error("message_id va content talab qilinadi")
            return

        message = await database_sync_to_async(get_object_or_404)(Message, id=message_id, chat_id=self.chat_id)
        if message.sender != self.scope['user']:
            await self.send_error("Faqat o‘zingizning xabaringizni tahrirlashingiz mumkin")
            return

        message.content = content
        message.is_edited = True
        await database_sync_to_async(message.save)()
        chat = await database_sync_to_async(get_object_or_404)(Chat, id=self.chat_id)
        await self.channel_layer.group_send(
            self.chat_group_name,
            {
                'type': 'chat_message',
                'action': 'edit',
                'message': MessageSerializer(message, context={'chat': chat, 'sender': self.scope['user']}).data
            }
        )

    async def delete_message(self, data):
        message_id = data.get('message_id')
        if not message_id:
            await self.send_error("message_id talab qilinadi")
            return

        message = await database_sync_to_async(get_object_or_404)(Message, id=message_id, chat_id=self.chat_id)
        if message.sender != self.scope['user']:
            await self.send_error("Faqat o‘zingizning xabaringizni o‘chirishingiz mumkin")
            return

        await database_sync_to_async(message.delete)()
        await self.channel_layer.group_send(
            self.chat_group_name,
            {
                'type': 'chat_message',
                'action': 'delete',
                'message_id': message_id
            }
        )

    async def add_reaction(self, data):
        message_id = data.get('message_id')
        reaction_value = data.get('reaction')
        if not message_id or not reaction_value:
            await self.send_error("message_id va reaction talab qilinadi")
            return

        message = await database_sync_to_async(get_object_or_404)(Message, id=message_id, chat_id=self.chat_id)
        reaction, created = await database_sync_to_async(Reaction.objects.get_or_create)(
            message=message, user=self.scope['user'], defaults={'reaction': reaction_value}
        )
        if not created:
            reaction.reaction = reaction_value
            await database_sync_to_async(reaction.save)()

        await self.channel_layer.group_send(
            self.chat_group_name,
            {
                'type': 'chat_message',
                'action': 'reaction_add',
                'message': MessageSerializer(message).data
            }
        )

    async def remove_reaction(self, data):
        message_id = data.get('message_id')
        if not message_id:
            await self.send_error("message_id talab qilinadi")
            return

        message = await database_sync_to_async(get_object_or_404)(Message, id=message_id, chat_id=self.chat_id)
        try:
            reaction = await database_sync_to_async(Reaction.objects.get)(message=message, user=self.scope['user'])
            await database_sync_to_async(reaction.delete)()
            await self.channel_layer.group_send(
                self.chat_group_name,
                {
                    'type': 'chat_message',
                    'action': 'reaction_remove',
                    'message': MessageSerializer(message).data
                }
            )
        except Reaction.DoesNotExist:
            await self.send_error("Reaksiya topilmadi")

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))