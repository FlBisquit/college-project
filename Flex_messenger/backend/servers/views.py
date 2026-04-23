from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

from .models import Server, ServerMember
from .serializers import ServerSerializer, ServerDetailSerializer, ServerMemberSerializer


class ServerListCreateView(APIView):
    """Список всех серверов / создать сервер"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Список всех серверов"""
        servers = Server.objects.all().select_related('owner')
        serializer = ServerSerializer(servers, many=True, context={'request': request})
        return Response(
            {'message': 'Список серверов', 'data': serializer.data},
            status=status.HTTP_200_OK
        )

    def post(self, request):
        """Создать сервер"""
        if request.user.owned_servers.count() >= 6:
            return Response(
                {'message': 'Вы не можете создать больше 6 серверов'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = ServerSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        server = serializer.save(owner=request.user)
        # владелец автоматически становится участником
        ServerMember.objects.create(
            server=server,
            user=request.user,
            role=ServerMember.Role.OWNER
        )

        return Response(
            {'message': 'Сервер успешно создан', 'data': serializer.data},
            status=status.HTTP_201_CREATED
        )


class MyServersView(APIView):
    """Получить мои серверы"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        servers = request.user.servers.all().select_related('owner')
        serializer = ServerSerializer(servers, many=True, context={'request': request})
        return Response(
            {'message': 'Ваши серверы', 'data': serializer.data},
            status=status.HTTP_200_OK
        )


class PublicServersView(APIView):
    """Получить публичные серверы"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        servers = Server.objects.filter(is_public=True).exclude(owner=request.user).select_related('owner')
        serializer = ServerSerializer(servers, many=True, context={'request': request})
        return Response(
            {'message': 'Публичные серверы', 'data': serializer.data},
            status=status.HTTP_200_OK
        )


class ServerDetailView(APIView):
    """Получить / обновить / удалить сервер"""
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        server = get_object_or_404(Server, pk=pk)
        serializer = ServerDetailSerializer(server, context={'request': request})
        return Response(
            {'message': 'Детали сервера', 'data': serializer.data},
            status=status.HTTP_200_OK
        )

    def patch(self, request, pk):
        server = get_object_or_404(Server, pk=pk)
        
        if server.owner != request.user:
            return Response(
                {'message': 'У вас нет прав для редактирования этого сервера'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = ServerSerializer(server, data=request.data, partial=True, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response(
            {'message': 'Сервер успешно обновлён', 'data': serializer.data},
            status=status.HTTP_200_OK
        )

    def put(self, request, pk):
        server = get_object_or_404(Server, pk=pk)
        
        if server.owner != request.user:
            return Response(
                {'message': 'У вас нет прав для редактирования этого сервера'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = ServerSerializer(server, data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response(
            {'message': 'Сервер успешно обновлён', 'data': serializer.data},
            status=status.HTTP_200_OK
        )

    def delete(self, request, pk):
        server = get_object_or_404(Server, pk=pk)
        
        if server.owner != request.user:
            return Response(
                {'message': 'У вас нет прав для удаления этого сервера'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        server.delete()
        return Response(
            {'message': 'Сервер успешно удалён'},
            status=status.HTTP_204_NO_CONTENT
        )


class JoinServerView(APIView):
    """Вступить на сервер"""
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        server = get_object_or_404(Server, pk=pk)

        # Проверяем приватный ли сервер
        if not server.is_public:
            return Response(
                {'message': 'Это приватный сервер'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Проверяем, не уже ли пользователь на сервере
        if ServerMember.objects.filter(server=server, user=request.user).exists():
            return Response(
                {'message': 'Вы уже являетесь участником этого сервера'},
                status=status.HTTP_409_CONFLICT
            )

        ServerMember.objects.create(server=server, user=request.user)
        serializer = ServerSerializer(server, context={'request': request})
        return Response(
            {'message': 'Вы успешно присоединились к серверу', 'data': serializer.data},
            status=status.HTTP_201_CREATED
        )


class LeaveServerView(APIView):
    """Покинуть сервер"""
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        server = get_object_or_404(Server, pk=pk)

        if server.owner == request.user:
            return Response(
                {'message': 'Владелец не может покинуть сервер'},
                status=status.HTTP_403_FORBIDDEN
            )

        membership = ServerMember.objects.filter(server=server, user=request.user)
        if not membership.exists():
            return Response(
                {'message': 'Вы не являетесь участником этого сервера'},
                status=status.HTTP_404_NOT_FOUND
            )

        membership.delete()
        return Response(
            {'message': 'Вы успешно покинули сервер'},
            status=status.HTTP_204_NO_CONTENT
        )


class ServerMembersView(APIView):
    """Список участников сервера"""
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        server = get_object_or_404(Server, pk=pk)
        members = ServerMember.objects.filter(server=server).select_related('user')
        serializer = ServerMemberSerializer(members, many=True, context={'request': request})
        
        return Response(
            {'message': 'Участники сервера', 'data': serializer.data},
            status=status.HTTP_200_OK
        )


class UpdateMemberRoleView(APIView):
    """Изменить роль участника (только для владельца/админа)"""
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk, user_id):
        server = get_object_or_404(Server, pk=pk)

        # проверяем права
        requester = get_object_or_404(ServerMember, server=server, user=request.user)
        if requester.role not in [ServerMember.Role.OWNER, ServerMember.Role.ADMIN]:
            return Response(
                {'message': 'У вас нет прав для изменения ролей участников'},
                status=status.HTTP_403_FORBIDDEN
            )

        member = get_object_or_404(ServerMember, server=server, user_id=user_id)
        new_role = request.data.get('role')

        if new_role not in [ServerMember.Role.ADMIN, ServerMember.Role.MEMBER]:
            return Response(
                {'message': 'Недопустимая роль'},
                status=status.HTTP_400_BAD_REQUEST
            )

        member.role = new_role
        member.save()
        return Response(
            {'message': 'Роль участника успешно обновлена', 'data': ServerMemberSerializer(member).data},
            status=status.HTTP_200_OK
        )