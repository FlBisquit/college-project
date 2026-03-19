from django.shortcuts import render
from django.http import HttpResponseRedirect, JsonResponse
from users.models import User
from .models import Chat, ChatData
import json
from redis import Redis
from users.views import is_authorized
from django.db import models
from django.contrib import messages

r = Redis()

def chating_main(request):
    if user := is_authorized(request):
        chats = Chat.objects.filter(
            done=False
        ).filter(
            models.Q(is_private=False) | models.Q(participants=user)
        ).distinct()
        return render(request, 'chats/chat.html', context={
            'user': user,
            'chats': chats,
        })
    return HttpResponseRedirect('/')


def chat_main(request):
    if user := is_authorized(request):
        chats = Chat.objects.filter(
            done=False
        ).filter(
            models.Q(is_private=False) | models.Q(participants=user)
        ).distinct()
        return render(request, 'users/users.html', context={
            'user': user,
            'chats': chats,
        })
    return HttpResponseRedirect('/')


def create_chat(request):
    if user := is_authorized(request):
        max_chaters = request.POST.get('max_chaters') or 12
        chatName = request.POST.get('chatName')
        chat_avatar = request.FILES.get('chat_avatar')
        is_private = request.POST.get('is_private') == 'on'
        
        chat = Chat.objects.create(
            owner=user,
            max_chaters=max_chaters,
            chat_avatar=chat_avatar,
            chatName=chatName,
            is_private=is_private
        )
        chat.participants.add(user)
        return HttpResponseRedirect('/users/') 
    return HttpResponseRedirect('/')


def delete_chat(request, chat_id):
    if user := is_authorized(request):
        Chat.objects.filter(id=chat_id).delete()
        return HttpResponseRedirect('/users/')
    return HttpResponseRedirect('/')


def join_to_chat(request, chat_id):
    if user := is_authorized(request):
        chat = Chat.objects.filter(id=chat_id).first()
        if not chat:
            messages.error(request, 'Чат не найден')
            return HttpResponseRedirect('/users/')
        
        if chat.is_private and user not in chat.participants.all():
            messages.error(request, 'У вас нет доступа к этому приватному чату')
            return HttpResponseRedirect('/users/')

        if not chat.is_private and user not in chat.participants.all():
            chat.participants.add(user)
        
        request.session['chat_id'] = chat_id
 
        return HttpResponseRedirect(f'/chatting/room/{chat.id}/')
    return HttpResponseRedirect('/')


def invite_to_chat(request, chat_id):
    if user := is_authorized(request):
        chat = Chat.objects.filter(id=chat_id).first()
        if not chat:
            messages.error(request, 'Чат не найден')
            return HttpResponseRedirect('/users/')

        if chat.owner != user:
            messages.error(request, 'Вы не владелец этого чата')
           
            return HttpResponseRedirect(f'/chatting/room/{chat.id}/')
        
        if request.method == 'POST':
            username = request.POST.get('username')
            try:
                invited_user = User.objects.get(login=username)
            except User.DoesNotExist:
                messages.error(request, 'Пользователь не найден')
                return HttpResponseRedirect(f'/chatting/room/{chat.id}/')
            
            if invited_user in chat.participants.all():
                messages.warning(request, 'Пользователь уже в чате')
            else:
                chat.participants.add(invited_user)
                messages.success(request, f'Пользователь {username} приглашён')
            
            return HttpResponseRedirect(f'/chatting/room/{chat.id}/')

        return render(request, 'chats/invite_form.html', {'chat': chat})
    return HttpResponseRedirect('/')


def get_chat(request, chat_id):
    if chat := r.get(chat_id):
        chat = json.loads(chat.decode())
    else:
        chat = Chat.objects.filter(id=chat_id).first()
        if chat:
            r.set(chat_id, json.dumps({
                "id": str(chat.id),
                "number": chat.number,
                "max_chaters": chat.max_chaters,
            }))
            chat = chat.data 
        else:
            chat = None
    if chat:
        return JsonResponse({'result': chat})
    return JsonResponse({'result': None})


def update_chat_data(request, chat_id):
    data = request.POST.get('data') or {}
    if chat := r.get(chat_id):
        chat = json.loads(chat.decode())
        chat.update(data)
        r.set(chat_id, json.dumps(chat))
    else:
        chat = Chat.objects.filter(id=chat_id).first()
        if chat:
            updated_data = chat.data 
            updated_data.update(data)
            chat.data = updated_data
            chat.save()
            r.set(chat_id, json.dumps(chat.data))
    return JsonResponse({'result': 'update success'})


def get_chat_list(request):
    chats = Chat.objects.all()
    result = [str(chat.id) for chat in chats]
    return JsonResponse({'result': result})