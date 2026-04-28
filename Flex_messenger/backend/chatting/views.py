from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from servers.models import Server


@login_required(login_url='/')
def room(request, chat_id):
    server = get_object_or_404(Server, id=server_id, done=False)

    if chat.is_private and request.user not in chat.participants.all():
        messages.error(request, 'У вас нет доступа к этому чату')
        return redirect('/users/')

    return render(request, 'chatting/room.html', {
        'chat': server,
        'user': request.user,
        'room_name': server_id,
    })