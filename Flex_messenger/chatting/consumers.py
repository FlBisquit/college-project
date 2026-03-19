import json
import base64
import uuid
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from django.core.files.base import ContentFile
from .models import Message
class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'
        self.user = self.scope['user']
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message_type = data.get('type', 'text')
            
            if message_type == 'text    ':
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
                            'created_at': str(await self.get_current_time())
                        }
                    )
            elif message_type == 'image':
                image_data = data.get('image_data')
                file_name = data.get('file_name', f'image_{uuid.uuid4()}.png')
                if image_data:
                    await self.save_image(image_data, file_name)
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'chat_message',
                            'image_data': image_data,
                            'file_name': file_name,
                            'author': self.user.username,
                            'message_type': 'image',
                            'created_at': str(await self.get_current_time())
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
                'author': event['author'],
                'created_at': event['created_at']
            }))

    @sync_to_async
    def save_message(self, text):
        from .models import Chat, Message
        from django.contrib.auth.models import User
        chat = Chat.objects.get(uuid=self.room_name)
        Message.objects.create(
            chat=chat,
            author=self.user,
            text=text
        )

    @sync_to_async
    def save_image(self, image_data, file_name):
        from chats.models import Chat
        from django.contrib.auth.models import User
        
        chat = Chat.objects.get(uuid=self.room_name)
        image_content = ContentFile(base64.b64decode(image_data), name=file_name)
        message = Message.objects.create(
            chat=chat,
            author=self.user,
            text=''
        )
        message.image.save(file_name, image_content, save=True)
        return message

    @sync_to_async
    def get_current_time(self):
        from django.utils import timezone
        return timezone.now()