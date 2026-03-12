from django.shortcuts import render
from chats.models import Chat
from django.http import HttpResponseRedirect, JsonResponse
from users.views import is_authorized

def room(request, room_name):
    if user := is_authorized(request):
        chat = Chat.objects.filter(id=room_name).first()
        if not chat:
            return HttpResponseRedirect('/chats/')
        return render(request, 'chatting/room.html', {
            'room_name': chat.id,
            'user': user
        })
    return HttpResponseRedirect('/')