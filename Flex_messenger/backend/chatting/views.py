from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from servers.models import Chat


@login_required(login_url='/')
def room(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id, done=False)

    if chat.is_private and request.user not in chat.participants.all():
        messages.error(request, 'У вас нет доступа к этому чату')
        return redirect('/users/')

    return render(request, 'chatting/room.html', {
        'chat': chat,
        'user': request.user,
        'room_name': chat_id,
    })