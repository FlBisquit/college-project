from django.shortcuts import render
from django.contrib.auth.decorators import login_required

def room(request, room_name):
    return render(request, 'chatting/room.html', {
        'room_name': room_name
    })