from django.shortcuts import render
from django.http import JsonResponse
from django.db import models

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from users.models import User
from users.views import is_authorized

from .models import Chat
from .serializers import ChatSerializer

import json
from redis import Redis

r = Redis()


class ChatListApiView(APIView):
    def get(self, request):
        user = is_authorized(request)
        if not user:
            return Response(
                {'error': 'незарегистрирован'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        chats = Chat.objects.filter(done=False).filter(
            models.Q(is_private=False) | models.Q(participants=user)
        ).distinct()

        serializer = ChatSerializer(chats, many=True)
        return Response(serializer.data)


class CreateChatApiView(APIView):
    def post(self, request):
        user = is_authorized(request)
        if not user:
            return Response(
                {'error': 'незарегистрирован'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        serializer = ChatSerializer(data=request.data)

        if serializer.is_valid():
            chat = serializer.save(owner=user)
            chat.participants.add(user)
            return Response(
                ChatSerializer(chat).data,
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DeleteChatAPIView(APIView):
    def delete(self, request, chat_id):
        user = is_authorized(request)
        if not user:
            return Response(
                {'error': 'незарегистрирован'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        chat = Chat.objects.filter(id=chat_id).first()
        if not chat:
            return Response(
                {'error': 'Чат не найден'},
                status=status.HTTP_404_NOT_FOUND
            )

        if chat.owner != user:
            return Response(
                {'error': 'Нет доступа'},
                status=status.HTTP_403_FORBIDDEN
            )

        chat.delete()
        return Response(
            {'message': 'Чат удален'},
            status=status.HTTP_204_NO_CONTENT
        )


class JoinToChatAPIView(APIView):
    def post(self, request, chat_id):
        user = is_authorized(request)
        if not user:
            return Response(
                {'error': 'незарегистрирован'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        chat = Chat.objects.filter(id=chat_id).first()
        if not chat:
            return Response(
                {'error': 'Чат не найден'},
                status=status.HTTP_404_NOT_FOUND
            )

        if chat.is_private and user not in chat.participants.all():
            return Response(
                {'error': 'Нет доступа к чату'},
                status=status.HTTP_403_FORBIDDEN
            )

        if user not in chat.participants.all():
            chat.participants.add(user)

        return Response(
            {'message': 'Успешный вход в чат'},
            status=status.HTTP_200_OK
        )


class InviteToChatAPIView(APIView):
    def post(self, request, chat_id):
        user = is_authorized(request)
        if not user:
            return Response(
                {'error': 'незарегистрирован'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        chat = Chat.objects.filter(id=chat_id).first()
        if not chat:
            return Response(
                {'error': 'Чат не найден'},
                status=status.HTTP_404_NOT_FOUND
            )

        if chat.owner != user:
            return Response(
                {'error': 'Нет доступа к добавлению пользователей'},
                status=status.HTTP_403_FORBIDDEN
            )

        username = request.data.get('username')

        try:
            invited_user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response(
                {'error': 'Пользователь не найден'},
                status=status.HTTP_404_NOT_FOUND
            )

        if invited_user in chat.participants.all():
            return Response(
                {'warning': 'Пользователь уже в чате'},
                status=status.HTTP_200_OK
            )

        chat.participants.add(invited_user)

        return Response(
            {'message': f'{username} приглашён'},
            status=status.HTTP_200_OK
        )


class GetChatAPIView(APIView):
    def get(self, request, chat_id):
        chat_data = r.get(chat_id)

        if chat_data:
            chat = json.loads(chat_data.decode())
        else:
            chat_obj = Chat.objects.filter(id=chat_id).first()
            if not chat_obj:
                return Response(
                    {'result': None},
                    status=status.HTTP_404_NOT_FOUND
                )

            chat = {
                "id": str(chat_obj.id),
                "number": chat_obj.number,
                "max_chaters": chat_obj.max_chaters,
            }

            r.set(chat_id, json.dumps(chat))

        return Response({'result': chat}, status=status.HTTP_200_OK)


class UpdateChatDataAPIView(APIView):
    def post(self, request, chat_id):
        data = request.data.get('data', {})

        chat_data = r.get(chat_id)

        if chat_data:
            chat = json.loads(chat_data.decode())
            chat.update(data)
            r.set(chat_id, json.dumps(chat))
            return Response({"result": chat}, status=status.HTTP_200_OK)

        chat_obj = Chat.objects.filter(id=chat_id).first()
        if not chat_obj:
            return Response(
                {'error': 'Чат не найден'},
                status=status.HTTP_404_NOT_FOUND
            )

        updated_data = chat_obj.data or {}
        updated_data.update(data)

        chat_obj.data = updated_data
        chat_obj.save()

        r.set(chat_id, json.dumps(updated_data))

        return Response({"result": updated_data}, status=status.HTTP_200_OK)