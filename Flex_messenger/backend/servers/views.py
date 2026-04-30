from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.core.cache import cache

from .models import Server, ServerMember
from .serializers import ServerSerializer, ServerDetailSerializer, ServerMemberSerializer


class ServerListCreateView(APIView):
    """Список всех серверов / создать сервер"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cache_key = f'servers:all_list_{request.user.id}'
        data = cache.get(cache_key)

        if data is None:
            servers = Server.objects.all().select_related('owner')
            serializer = ServerSerializer(servers, many=True, context={'request': request})
            data = serializer.data
            cache.set(cache_key, data, 300)

        return Response({'message': 'Список серверов', 'data': data}, status=status.HTTP_200_OK)

    def post(self, request):
        if request.user.owned_servers.count() >= 5:
            return Response(
                {'message': 'Вы не можете создать больше 5 серверов'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = ServerSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        server = serializer.save(owner=request.user)
        ServerMember.objects.create(server=server, user=request.user, role=ServerMember.Role.OWNER)

        cache.delete(f'servers:all_list_{request.user.id}')
        cache.delete(f'servers:public_list_{request.user.id}')
        cache.delete(f'servers:user_{request.user.id}_list')

        return Response({'message': 'Сервер успешно создан', 'data': serializer.data}, status=status.HTTP_201_CREATED)


class MyServersView(APIView):
    """Получить мои серверы"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cache_key = f'servers:user_{request.user.id}_list'
        data = cache.get(cache_key)

        if data is None:
            servers = request.user.servers.all().select_related('owner')
            serializer = ServerSerializer(servers, many=True, context={'request': request})
            data = serializer.data
            cache.set(cache_key, data, 300)

        return Response({'message': 'Ваши серверы', 'data': data}, status=status.HTTP_200_OK)


class PublicServersView(APIView):
    """Получить публичные серверы"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cache_key = f'servers:public_list_{request.user.id}'
        data = cache.get(cache_key)

        if data is None:
            servers = Server.objects.filter(is_public=True).exclude(owner=request.user).select_related('owner')
            serializer = ServerSerializer(servers, many=True, context={'request': request})
            data = serializer.data
            cache.set(cache_key, data, 30)  # 30 секунд

        return Response({'message': 'Публичные серверы', 'data': data}, status=status.HTTP_200_OK)


class ServerDetailView(APIView):
    """Получить / обновить / удалить сервер"""
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        cache_key = f'server:detail_{pk}_{request.user.id}'
        data = cache.get(cache_key)

        if data is None:
            server = get_object_or_404(Server, pk=pk)
            serializer = ServerDetailSerializer(server, context={'request': request})
            data = serializer.data
            cache.set(cache_key, data, 600)

        return Response({'message': 'Детали сервера', 'data': data}, status=status.HTTP_200_OK)

    def patch(self, request, pk):
        server = get_object_or_404(Server, pk=pk)

        if server.owner != request.user:
            return Response({'message': 'У вас нет прав для редактирования этого сервера'}, status=status.HTTP_403_FORBIDDEN)

        serializer = ServerSerializer(server, data=request.data, partial=True, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        self._invalidate_server_cache(pk, owner_id=server.owner.id)

        return Response({'message': 'Сервер успешно обновлён', 'data': serializer.data}, status=status.HTTP_200_OK)

    def put(self, request, pk):
        server = get_object_or_404(Server, pk=pk)

        if server.owner != request.user:
            return Response({'message': 'У вас нет прав для редактирования этого сервера'}, status=status.HTTP_403_FORBIDDEN)

        serializer = ServerSerializer(server, data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        self._invalidate_server_cache(pk, owner_id=server.owner.id)

        return Response({'message': 'Сервер успешно обновлён', 'data': serializer.data}, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        server = get_object_or_404(Server, pk=pk)

        if server.owner != request.user:
            return Response({'message': 'У вас нет прав для удаления этого сервера'}, status=status.HTTP_403_FORBIDDEN)

        owner_id = server.owner.id
        server.delete()

        self._invalidate_server_cache(pk, owner_id=owner_id)

        return Response({'message': 'Сервер успешно удалён'}, status=status.HTTP_204_NO_CONTENT)

    @staticmethod
    def _invalidate_server_cache(server_id, owner_id=None):
        cache.delete(f'server:detail_{server_id}')
        if owner_id:
            cache.delete(f'server:detail_{server_id}_{owner_id}')
            cache.delete(f'servers:all_list_{owner_id}')
            cache.delete(f'servers:public_list_{owner_id}')
            cache.delete(f'servers:user_{owner_id}_list')


class JoinServerView(APIView):
    """Вступить на сервер"""
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        server = get_object_or_404(Server, pk=pk)

        if not server.is_public:
            return Response({'message': 'Это приватный сервер'}, status=status.HTTP_403_FORBIDDEN)

        if ServerMember.objects.filter(server=server, user=request.user).exists():
            return Response({'message': 'Вы уже являетесь участником этого сервера'}, status=status.HTTP_409_CONFLICT)

        if server.server_members.count() >= server.max_members:
            return Response({'message': 'Сервер достиг максимального количества участников'}, status=status.HTTP_403_FORBIDDEN)

        ServerMember.objects.create(server=server, user=request.user)

        cache.delete(f'servers:user_{request.user.id}_list')
        cache.delete(f'servers:all_list_{request.user.id}')
        cache.delete(f'servers:public_list_{request.user.id}')
        cache.delete(f'servers:public_list_{server.owner.id}')
        cache.delete(f'server:detail_{pk}')
        cache.delete(f'server:detail_{pk}_{request.user.id}')
        cache.delete(f'server:members_{pk}')

        serializer = ServerSerializer(server, context={'request': request})
        return Response({'message': 'Вы успешно присоединились к серверу', 'data': serializer.data}, status=status.HTTP_201_CREATED)


class LeaveServerView(APIView):
    """Покинуть сервер"""
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        server = get_object_or_404(Server, pk=pk)

        if server.owner == request.user:
            return Response({'message': 'Владелец не может покинуть сервер'}, status=status.HTTP_403_FORBIDDEN)

        membership = ServerMember.objects.filter(server=server, user=request.user)
        if not membership.exists():
            return Response({'message': 'Вы не являетесь участником этого сервера'}, status=status.HTTP_404_NOT_FOUND)

        membership.delete()

        cache.delete(f'servers:user_{request.user.id}_list')
        cache.delete(f'servers:all_list_{request.user.id}')
        cache.delete(f'servers:public_list_{request.user.id}')
        cache.delete(f'servers:public_list_{server.owner.id}')
        cache.delete(f'server:detail_{pk}')
        cache.delete(f'server:detail_{pk}_{request.user.id}')
        cache.delete(f'server:members_{pk}')

        return Response({'message': 'Вы успешно покинули сервер'}, status=status.HTTP_204_NO_CONTENT)


class ServerMembersView(APIView):
    """Список участников сервера"""
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        cache_key = f'server:members_{pk}'
        data = cache.get(cache_key)

        if data is None:
            server = get_object_or_404(Server, pk=pk)
            members = ServerMember.objects.filter(server=server).select_related('user')
            serializer = ServerMemberSerializer(members, many=True, context={'request': request})
            data = serializer.data
            cache.set(cache_key, data, 300)

        return Response({'message': 'Участники сервера', 'data': data}, status=status.HTTP_200_OK)


class UpdateMemberRoleView(APIView):
    """Изменить роль участника (только для владельца/админа)"""
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk, user_id):
        server = get_object_or_404(Server, pk=pk)

        requester = get_object_or_404(ServerMember, server=server, user=request.user)
        if requester.role not in [ServerMember.Role.OWNER, ServerMember.Role.ADMIN]:
            return Response({'message': 'У вас нет прав для изменения ролей участников'}, status=status.HTTP_403_FORBIDDEN)

        member = get_object_or_404(ServerMember, server=server, user_id=user_id)
        new_role = request.data.get('role')

        if new_role not in [ServerMember.Role.ADMIN, ServerMember.Role.MEMBER]:
            return Response({'message': 'Недопустимая роль'}, status=status.HTTP_400_BAD_REQUEST)

        member.role = new_role
        member.save()

        cache.delete(f'server:members_{pk}')

        return Response(
            {'message': 'Роль участника успешно обновлена', 'data': ServerMemberSerializer(member).data},
            status=status.HTTP_200_OK
        )