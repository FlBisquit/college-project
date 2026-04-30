from rest_framework import serializers
from .models import Message


class MessageSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(source='author.username', read_only=True)
    author_avatar = serializers.CharField(source='author.avatar_url', read_only=True)

    class Meta:
        model = Message
        fields = [
            'id',
            'server',
            'author',
            'author_username',
            'author_avatar',
            'text',
            'image',
            'created_at',
        ]
        read_only_fields = ['id', 'author', 'created_at']

    def validate(self, attrs):
        if not attrs.get('text') and not attrs.get('image'):
            raise serializers.ValidationError('Сообщение должно содержать текст или изображение.')
        return attrs

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)