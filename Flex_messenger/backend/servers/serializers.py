from rest_framework import serializers
from .models import Chat, ChatData

class ChatSerializer(serializers.ModelSerializer):
    class Meta:
        model:Chat
        fields = ['id','number','owner','participants','max_chaters','done','started','chatName','chat_avatar','is_private']

class ChatDataSerializer(serializers.ModelSerializer):
    class Meta:
        model:ChatData
        fields = ['owner','user','data']