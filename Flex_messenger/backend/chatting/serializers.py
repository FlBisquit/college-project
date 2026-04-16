# ченелс
from channels.generic.websocket import AsyncWebsocketConsumer
# импорты функций
import json
import base64
import uuid
from asgiref.sync import sync_to_async
from django.core.files.base import ContentFile
from django.utils.timezone import now
# импорты моделей
from .models import Chat, Message

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'
        self.user = self.scope['user']
        if not self.user.is_authenticated:
            await self.close()
            return
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message_type = data.get('type', 'text')

            if message_type == 'text':
                message = data.get('message', '').strip()
                if message:
                    await self.save_message(message)
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'chat_message',
                            'message': message,
                            'author': self.user.username,
                            'message_type': 'text',
                            'created_at': str(now())
                        }
                    )

            elif message_type == 'image':
                image_data = data.get('image_data')
                file_name = data.get('file_name', f'image_{uuid.uuid4()}.png')
                mime = data.get('mime', 'image/png')

                if image_data:
                    await self.save_image(image_data, file_name)
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'chat_message',
                            'image_data': image_data,
                            'file_name': file_name,
                            'mime': mime,
                            'author': self.user.username,
                            'message_type': 'image',
                            'created_at': str(now())
                        }
                    )

        except json.JSONDecodeError:
            pass

    async def chat_message(self, event):
        message_type = event.get('message_type', 'text')
        if message_type == 'text':
            await self.send(text_data=json.dumps({
                'type': 'text',
                'message': event['message'],
                'author': event['author'],
                'created_at': event['created_at']
            }))
        elif message_type == 'image':
            await self.send(text_data=json.dumps({
                'type': 'image',
                'image_data': event['image_data'],
                'file_name': event['file_name'],
                'mime': event.get('mime', 'image/png'),
                'author': event['author'],
                'created_at': event['created_at']
            }))

    async def save_message(self, text):
        try:
            chat = await sync_to_async(Chat.objects.get)(id=self.room_name)
            await sync_to_async(Message.objects.create)(
                chat=chat,
                author_id=self.user.id,
                text=text
            )
        except Chat.DoesNotExist:
            pass

    async def save_image(self, image_data, file_name):
        try:
            chat = await sync_to_async(Chat.objects.get)(id=self.room_name)
            image_content = ContentFile(
                base64.b64decode(image_data),
                name=file_name
            )
            message = await sync_to_async(Message.objects.create)(
                chat=chat,
                author_id=self.user.id,
                text=''
            )
            await sync_to_async(message.image.save)(
                file_name,
                image_content,
                True
            )
            return message
        except Chat.DoesNotExist:
            pass