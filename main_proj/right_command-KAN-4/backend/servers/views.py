from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

from .models import Server, ServerMember
from .serializers import ServerSerializer, ServerDetailSerializer, ServerMemberSerializer


class ServerListCreateView(generics.ListCreateAPIView):
    """Список серверов / создать сервер"""
    permission_classes = [IsAuthenticated]
    serializer_class = ServerSerializer

    def get_queryset(self):
        return Server.objects.all().select_related('owner')

    def perform_create(self, serializer):
        server = serializer.save(owner=self.request.user)
        # владелец автоматически становится участником
        ServerMember.objects.create(
            server=server,
            user=self.request.user,
            role=ServerMember.Role.OWNER
        )


class ServerDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Получить / обновить / удалить сервер"""
    permission_classes = [IsAuthenticated]
    queryset = Server.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ServerDetailSerializer
        return ServerSerializer

    def update(self, request, *args, **kwargs):
        server = self.get_object()
        if server.owner != request.user:
            return Response({'detail': 'Нет прав'}, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        server = self.get_object()
        if server.owner != request.user:
            return Response({'detail': 'Нет прав'}, status=status.HTTP_403_FORBIDDEN)
        server.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class JoinServerView(APIView):
    """Вступить на сервер"""
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        server = get_object_or_404(Server, pk=pk)

        if ServerMember.objects.filter(server=server, user=request.user).exists():
            return Response({'detail': 'Вы уже на сервере'}, status=status.HTTP_400_BAD_REQUEST)

        ServerMember.objects.create(server=server, user=request.user)
        return Response({'detail': 'Вы вступили на сервер'}, status=status.HTTP_201_CREATED)


class LeaveServerView(APIView):
    """Покинуть сервер"""
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        server = get_object_or_404(Server, pk=pk)

        if server.owner == request.user:
            return Response({'detail': 'Владелец не может покинуть сервер'}, status=status.HTTP_400_BAD_REQUEST)

        ServerMember.objects.filter(server=server, user=request.user).delete()
        return Response({'detail': 'Вы покинули сервер'})


class ServerMembersView(generics.ListAPIView):
    """Список участников сервера"""
    permission_classes = [IsAuthenticated]
    serializer_class = ServerMemberSerializer

    def get_queryset(self):
        server = get_object_or_404(Server, pk=self.kwargs['pk'])
        return ServerMember.objects.filter(server=server).select_related('user')


class UpdateMemberRoleView(APIView):
    """Изменить роль участника (только для владельца/админа)"""
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk, user_id):
        server = get_object_or_404(Server, pk=pk)

        # проверяем права
        requester = get_object_or_404(ServerMember, server=server, user=request.user)
        if requester.role not in [ServerMember.Role.OWNER, ServerMember.Role.ADMIN]:
            return Response({'detail': 'Нет прав'}, status=status.HTTP_403_FORBIDDEN)

        member = get_object_or_404(ServerMember, server=server, user_id=user_id)
        new_role = request.data.get('role')

        if new_role not in [ServerMember.Role.ADMIN, ServerMember.Role.MEMBER]:
            return Response({'detail': 'Недопустимая роль'}, status=status.HTTP_400_BAD_REQUEST)

        member.role = new_role
        member.save()
        return Response(ServerMemberSerializer(member).data)