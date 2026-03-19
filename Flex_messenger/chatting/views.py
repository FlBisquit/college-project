from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from chats.models import Chat
from users.views import is_authorized

def room(request, chat_id):
    user = is_authorized(request)
    if not user:
        return redirect('/')
    
    chat = get_object_or_404(Chat, id=chat_id, done=False)
    
    if chat.is_private and user not in chat.participants.all():
        messages.error(request, 'У вас нет доступа к этому чату')
        return redirect('/users/')
    
    return render(request, 'chatting/room.html', {
        'chat': chat,
        'user': user,
        'room_name': chat_id,  
    })