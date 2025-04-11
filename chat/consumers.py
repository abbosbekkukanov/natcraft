import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Chat, Message, Reaction
from .serializers import MessageSerializer, ReactionSerializer, MinimalMessageSerializer
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
from products.models import Product

logger = logging.getLogger(__name__)

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.chat_id = self.scope['url_route']['kwargs']['chat_id']
        self.chat_group_name = f'chat_{self.chat_id}'
        
        logger.info(f"WebSocket ulanish boshlandi: chat_id={self.chat_id}, "
                   f"user={self.scope['user'].email if not self.scope['user'].is_anonymous else 'anonymous'}")

        if self.scope['user'].is_anonymous:
            logger.error(f"Anonim foydalanuvchi ulanishga urindi: chat_id={self.chat_id}")
            await self.close(code=4001)
            return

        try:
            participant_check = await self.is_chat_participant()
            logger.info(f"Chat ishtirokchisi tekshiruvi: chat_id={self.chat_id}, "
                       f"user_id={self.scope['user'].id}, result={participant_check}")
            if participant_check:
                await self.channel_layer.group_add(self.chat_group_name, self.channel_name)
                await self.accept()
                logger.info(f"Ulanish muvaffaqiyatli: chat_id={self.chat_id}, channel_name={self.channel_name}")
            else:
                logger.error(f"Foydalanuvchi chat ishtirokchisi emas: chat_id={self.chat_id}, "
                            f"user_id={self.scope['user'].id}")
                await self.close(code=4003)
        except Exception as e:
            logger.error(f"Ulanishda xato: chat_id={self.chat_id}, error={str(e)}")
            await self.close(code=1011)

    async def disconnect(self, close_code):
        logger.info(f"WebSocket yopildi: chat_id={self.chat_id}, code={close_code}, "
                   f"channel_name={self.channel_name if hasattr(self, 'channel_name') else 'not_set'}")
        if hasattr(self, 'chat_group_name'):
            await self.channel_layer.group_discard(self.chat_group_name, self.channel_name)

    async def receive(self, text_data):
        logger.info(f"Xabar qabul qilindi: chat_id={self.chat_id}, raw_data={text_data}")
        try:
            data = json.loads(text_data)
            action = data.get('action')
            logger.info(f"Xabar parse qilindi: chat_id={self.chat_id}, action={action}, data={data}")
            if not action:
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
                'reply_message': self.reply_message,
            }

            handler = handlers.get(action)
            if handler:
                await handler(data)
            else:
                await self.send_error("Noto‘g‘ri action")
        except json.JSONDecodeError as e:
            await self.send_error(f"Xato JSON formati: {str(e)}")
        except Exception as e:
            await self.send_error(f"Server ichki xatosi: {str(e)}")

    async def send_error(self, message):
        logger.info(f"Xato xabari yuborildi: chat_id={self.chat_id}, message={message}")
        await self.send(text_data=json.dumps({'error': message}))

    @database_sync_to_async
    def is_chat_participant(self):
        chat = get_object_or_404(Chat, id=self.chat_id)
        user = self.scope['user']
        return user == chat.seller or user == chat.buyer

    async def send_message(self, data):
        content = data.get('content')
        product_id = data.get('product')
        reply_to_id = data.get('reply_to')
        if not content:
            await self.send_error("Xabar matni talab qilinadi")
            return

        chat = await database_sync_to_async(get_object_or_404)(Chat, id=self.chat_id)
        message_data = {'content': content}
        if product_id:
            message_data['product'] = product_id
        if reply_to_id:
            message_data['reply_to'] = reply_to_id

        serializer = MessageSerializer(data=message_data, context={'chat': chat, 'sender': self.scope['user']})
        if await database_sync_to_async(serializer.is_valid)():
            message = await database_sync_to_async(serializer.save)()
            serialized_message = await database_sync_to_async(
                lambda: MessageSerializer(message, context={'chat': chat, 'sender': self.scope['user']}).data
            )()
            logger.info(f"Xabar saqlandi va yuborildi: chat_id={self.chat_id}, message_id={message.id}")
            await self.channel_layer.group_send(
                self.chat_group_name,
                {'type': 'chat_message', 'action': 'new', 'message': serialized_message}
            )
        else:
            await self.send_error(f"Xabar yuborishda xato: {await database_sync_to_async(lambda: serializer.errors)()}")

    async def sync_message(self, data):
        message_id = data.get('message_id')
        if not message_id:
            await self.send_error("message_id talab qilinadi")
            return

        message = await database_sync_to_async(get_object_or_404)(Message, id=message_id, chat_id=self.chat_id)
        serialized_message = await database_sync_to_async(
            lambda: MessageSerializer(message, context={'chat': message.chat}).data
        )()
        logger.info(f"Xabar sinxronlashtirildi: chat_id={self.chat_id}, message_id={message.id}")
        await self.channel_layer.group_send(
            self.chat_group_name,
            {'type': 'chat_message', 'action': 'new', 'message': serialized_message}
        )

    async def reply_message(self, data):
        message_id = data.get('message_id')
        content = data.get('content')
        if not message_id or not content:
            await self.send_error("message_id va content talab qilinadi")
            return

        chat = await database_sync_to_async(get_object_or_404)(Chat, id=self.chat_id)
        reply_to = await database_sync_to_async(get_object_or_404)(Message, id=message_id, chat_id=self.chat_id)
        message_data = {'content': content, 'reply_to': message_id}

        serializer = MessageSerializer(data=message_data, context={'chat': chat, 'sender': self.scope['user']})
        if await database_sync_to_async(serializer.is_valid)():
            message = await database_sync_to_async(serializer.save)()
            serialized_message = await database_sync_to_async(
                lambda: MessageSerializer(message, context={'chat': chat, 'sender': self.scope['user']}).data
            )()
            logger.info(f"Javob xabari saqlandi: chat_id={self.chat_id}, message_id={message.id}, reply_to={message_id}")
            await self.channel_layer.group_send(
                self.chat_group_name,
                {
                    'type': 'chat_message',
                    'action': 'reply',
                    'message': serialized_message
                }
            )
        else:
            await self.send_error(f"Javob yuborishda xato: {await database_sync_to_async(lambda: serializer.errors)()}")

    async def edit_message(self, data):
        message_id = data.get('message_id')
        content = data.get('content')
        if not message_id or not content:
            await self.send_error("message_id va content talab qilinadi")
            return

        message = await database_sync_to_async(get_object_or_404)(Message, id=message_id, chat_id=self.chat_id)
        sender = await database_sync_to_async(lambda: message.sender)()
        if message.sender != self.scope['user']:
            await self.send_error("Faqat o‘zingizning xabaringizni tahrirlashingiz mumkin")
            return

        message.content = content
        message.is_edited = True
        await database_sync_to_async(message.save)()
        serialized_message = await database_sync_to_async(
            lambda: MinimalMessageSerializer(message, context={'chat': message.chat}).data
        )()
        logger.info(f"Xabar tahrirlandi: chat_id={self.chat_id}, message_id={message.id}")
        await self.channel_layer.group_send(
            self.chat_group_name,
            {'type': 'chat_message', 'action': 'edit', 'message': serialized_message}
        )

    async def delete_message(self, data):
        message_id = data.get('message_id')
        if not message_id:
            await self.send_error("message_id talab qilinadi")
            return

        message = await database_sync_to_async(get_object_or_404)(Message, id=message_id, chat_id=self.chat_id)
        sender = await database_sync_to_async(lambda: message.sender)()
        if message.sender != self.scope['user']:
            await self.send_error("Faqat o‘zingizning xabaringizni o‘chirishingiz mumkin")
            return

        await database_sync_to_async(message.delete)()
        logger.info(f"Xabar o‘chirildi: chat_id={self.chat_id}, message_id={message_id}")
        await self.channel_layer.group_send(
            self.chat_group_name,
            {'type': 'chat_message', 'action': 'delete', 'message_id': message_id}
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
        serialized_message = await database_sync_to_async(
            lambda: MessageSerializer(message, context={'chat': message.chat}).data
        )()
        logger.info(f"Reaksiya qo‘shildi: chat_id={self.chat_id}, message_id={message_id}")
        await self.channel_layer.group_send(
            self.chat_group_name,
            {'type': 'chat_message', 'action': 'reaction_add', 'message': serialized_message}
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
            serialized_message = await database_sync_to_async(
                lambda: MessageSerializer(message, context={'chat': message.chat}).data
            )()
            logger.info(f"Reaksiya o‘chirildi: chat_id={self.chat_id}, message_id={message_id}")
            await self.channel_layer.group_send(
                self.chat_group_name,
                {'type': 'chat_message', 'action': 'reaction_remove', 'message': serialized_message}
            )
        except Reaction.DoesNotExist:
            await self.send_error("Reaksiya topilmadi")

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

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
        logger.info(f"{'Yangi chat yaratildi' if created else 'Mavjud chat qaytarildi'}: chat_id={chat.id}")
        await self.send(text_data=json.dumps({'action': 'chat_created', 'chat_id': chat.id}))