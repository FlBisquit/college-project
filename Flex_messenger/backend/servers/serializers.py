from rest_framework import serializers
from .models import Server, ServerMember
from users.serializers import UserSerializer, validate_avatar_file


class ServerMemberSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = ServerMember
        fields = ['id', 'user', 'role', 'joined_at']
        read_only_fields = ['id', 'joined_at']


class ServerSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    avatar_url = serializers.SerializerMethodField()
    members_count = serializers.SerializerMethodField()
    is_owner = serializers.SerializerMethodField()

    class Meta:
        model = Server
        fields = [
            'id',
            'name',
            'description',
            'avatar',
            'avatar_url',
            'max_members',
            'owner',
            'members_count',
            'is_owner',
            'is_public',
            'created_at'
        ]
        read_only_fields = ['id', 'owner', 'created_at']

    def get_avatar_url(self, obj):
        """Возвращает абсолютный URL аватара"""
        if obj.avatar:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.avatar.url)
            return obj.avatar.url
        return None

    def get_members_count(self, obj):
        return obj.server_members.count()

    def get_is_owner(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.owner == request.user
        return False

    def validate_max_members(self, value):
        if value > 12:
            raise serializers.ValidationError('Максимальное количество участников не может превышать 12.')
        return value

    def validate_avatar(self, value):
        return validate_avatar_file(value)


class ServerDetailSerializer(ServerSerializer):
    """Детальный сериализатор — включает список участников"""
    members = ServerMemberSerializer(source='server_members', many=True, read_only=True)

    class Meta(ServerSerializer.Meta):
        fields = ServerSerializer.Meta.fields + ['members']