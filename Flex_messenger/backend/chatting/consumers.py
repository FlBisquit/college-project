import json
import base64
import uuid

from channels.generic.websocket import AsyncWebsocketConsumer
from django.utils.timezone import now
from django.core.files.base import ContentFile
from asgiref.sync import sync_to_async

from .models import Server, Message
from users.models import User


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'
        self.user = self.scope['user']

        if not self.user.is_authenticated:
            await self.close()
            return

        self.server = await sync_to_async(Server.objects.get)(id=self.room_name)

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
                            'created_at': str(now())
                        }
                    )

        except json.JSONDecodeError:
            pass

    async def chat_message(self, event):
        if event.get('message_type') == 'text':
            await self.send(text_data=json.dumps({
                'type': 'text',
                'message': event['message'],
                'author': event['author'],
                'created_at': event['created_at']
            }))

        elif event.get('message_type') == 'image':
            await self.send(text_data=json.dumps({
                'type': 'image',
                'image_data': event['image_data'],
                'file_name': event['file_name'],
                'author': event['author'],
                'created_at': event['created_at']
            }))

    async def save_message(self, text):
        await sync_to_async(Message.objects.create)(
            server=self.server,
            author_id=self.user.id,
            text=text
        )

    async def save_image(self, image_data, file_name):
        image_content = ContentFile(
            base64.b64decode(image_data),
            name=file_name
        )

        message = await sync_to_async(Message.objects.create)(
            server=self.server,
            author_id=self.user.id,
            text=''
        )

        await sync_to_async(message.image.save)(
            file_name,
            image_content,
            True
        )

        return message

    async def command(self, command, args):
        if command == "kick":
            username = args

            owner = await sync_to_async(lambda: self.server.owner)()

            if self.user != owner:
                await self.send(text_data=json.dumps({
                    "type": "error",
                    "message": "Нужно быть владельцем сервера"
                }))
                return

            try:
                user_to_kick = await sync_to_async(User.objects.get)(username=username)
            except User.DoesNotExist:
                await self.send(text_data=json.dumps({
                    "type": "error",
                    "message": f"User {username} not found"
                }))
                return

            await sync_to_async(self.server.members.remove)(user_to_kick)

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "user_kicked",
                    "username": username,
                }
            )