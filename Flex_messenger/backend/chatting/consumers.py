import json
import base64
import uuid
import asyncio

from channels.generic.websocket import AsyncWebsocketConsumer
from django.utils.timezone import now
from django.core.files.base import ContentFile
from asgiref.sync import sync_to_async

from .models import Server, Message
from users.models import User

# Глобальный трекер онлайн-пользователей: {room_group_name: {username: connection_count}}
online_users = {}
online_users_lock = asyncio.Lock()


def get_avatar_url_sync(user):
    """Синхронная helper-функция для получения avatar_url"""
    return user.avatar_url()


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'
        self.user = self.scope['user']

        if not self.user.is_authenticated:
            await self.close()
            return

        # Получаем сервер с prefetched owner
        self.server = await sync_to_async(
            lambda: Server.objects.select_related('owner').get(id=self.room_name)
        )()
        self._owner = self.server.owner  # кэшируем объект owner

        # Учитываем подключение пользователя
        async with online_users_lock:
            room_online = online_users.setdefault(self.room_group_name, {})
            prev_count = room_online.get(self.user.username, 0)
            room_online[self.user.username] = prev_count + 1
            is_first_connection = (prev_count == 0)

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        # Отправляем текущему клиенту список онлайн-пользователей
        await self.send_user_list()

        # Уведомляем других о новом онлайн-пользователе
        if is_first_connection:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_joined',
                    'user': {
                        'username': self.user.username,
                        'avatar': await sync_to_async(get_avatar_url_sync)(self.user),
                        'is_owner': self.user == self._owner
                    }
                }
            )

    async def disconnect(self, close_code):
        # Сначала убираем из группы, чтобы не получать свои же события
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

        # Обновляем счётчик подключений
        should_notify_left = False
        async with online_users_lock:
            if self.room_group_name in online_users:
                room_online = online_users[self.room_group_name]
                if self.user.username in room_online:
                    room_online[self.user.username] -= 1
                    if room_online[self.user.username] <= 0:
                        del room_online[self.user.username]
                        should_notify_left = True
                    if not room_online:
                        del online_users[self.room_group_name]

        # Уведомляем остальных о выходе
        if should_notify_left:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_left',
                    'username': self.user.username
                }
            )

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
                            'author_avatar': await sync_to_async(get_avatar_url_sync)(self.user),
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
                            'author_avatar': await sync_to_async(get_avatar_url_sync)(self.user),
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
                'author_avatar': event.get('author_avatar'),
                'created_at': event['created_at']
            }))

        elif event.get('message_type') == 'image':
            await self.send(text_data=json.dumps({
                'type': 'image',
                'image_data': event['image_data'],
                'file_name': event['file_name'],
                'author': event['author'],
                'author_avatar': event.get('author_avatar'),
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

    async def send_user_list(self):
        # Снимок онлайн-пользователей под блокировкой
        async with online_users_lock:
            room_online = online_users.get(self.room_group_name, {})
            usernames = list(room_online.keys())

        users_data = []
        if usernames:
            # Загружаем пользователей из БД (один запрос)
            users_qs = await sync_to_async(lambda: list(User.objects.filter(username__in=usernames)))()
            for u in users_qs:
                users_data.append({
                    'username': u.username,
                    'avatar': await sync_to_async(get_avatar_url_sync)(u),
                    'is_owner': u == self._owner
                })

        await self.send(text_data=json.dumps({
            'type': 'user_list',
            'users': users_data
        }))

    async def user_joined(self, event):
        await self.send(text_data=json.dumps({
            'type': 'user_joined',
            'user': event['user']
        }))

    async def user_left(self, event):
        await self.send(text_data=json.dumps({
            'type': 'user_left',
            'username': event['username']
        }))

    async def command(self, command, args):
        if command == "kick":
            username = args

            if self.user != self._owner:
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
