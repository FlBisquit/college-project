from rest_framework import serializers
from .models import Server, ServerMember
from users.serializers import UserSerializer


class ServerMemberSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = ServerMember
        fields = ['id', 'user', 'role', 'joined_at']
        read_only_fields = ['id', 'joined_at']


class ServerSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    members_count = serializers.SerializerMethodField()

    class Meta:
        model = Server
        fields = ['id', 'name', 'description', 'avatar', 'owner', 'members_count', 'created_at']
        read_only_fields = ['id', 'owner', 'created_at']

    def get_members_count(self, obj):
        return obj.server_members.count()


class ServerDetailSerializer(ServerSerializer):
    """Детальный сериализатор — включает список участников"""
    members = ServerMemberSerializer(source='server_members', many=True, read_only=True)

    class Meta(ServerSerializer.Meta):
        fields = ServerSerializer.Meta.fields + ['members']