from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from servers.models import Server
from .models import Message
from .serializers import MessageSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def message_history(request, room_name):
    messages = Message.objects.filter(server_id=room_name).select_related('author')
    serializer = MessageSerializer(messages, many=True, context={'request': request})
    return Response(serializer.data)