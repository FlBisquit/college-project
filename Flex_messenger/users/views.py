from django.shortcuts import render, HttpResponseRedirect
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from .models import User
from chats.models import Chat

def user_profile(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/')
    hidden_password = '*' * 8
    return render(request, 'users/profile.html', context={
        'user': request.user,
        'hidden_password': hidden_password,
    })

def change_user(request):
    return render(request, 'users/change.html')

def change_name(request):
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return HttpResponseRedirect('/')
        password = request.POST.get('password')
        new_login = request.POST.get('new_login')
        user = authenticate(request, username=request.user.username, password=password)
        if not user:
            return HttpResponse('неверный пароль')
        if User.objects.filter(username=new_login).exists():
            return HttpResponse('такой ник уже занят')
        user.username = new_login
        user.save()
        return HttpResponseRedirect('/users/')

def change_password(request):
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return HttpResponseRedirect('/')
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        user = authenticate(request, username=request.user.username, password=old_password)
        if not user:
            return HttpResponse('неверный пароль')
        user.set_password(new_password)
        user.save()
        auth_login(request, user)

        return HttpResponseRedirect('/users/')

def change_avatar(request):
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return HttpResponseRedirect('/')

        new_avatar = request.FILES.get('new_avatar')
        if not new_avatar:
            return HttpResponse('файл не выбран')

        request.user.avatar = new_avatar
        request.user.save()

        return HttpResponseRedirect('/users/')

def users_index(request):
    return render(request, 'users/index.html')

def users_main(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/')

    chats = Chat.objects.all()
    return render(request, 'users/users.html', context={
        'user': request.user,
        'chats': chats,
    })

def registrate(request):
    if request.method == 'POST':
        login = request.POST.get('login')
        password = request.POST.get('password')
        password_test = request.POST.get('password2')
        email = request.POST.get('email')
        avatar = request.FILES.get('avatar')
        if User.objects.filter(username=login).exists():
            return HttpResponse('пользователь уже существует')
        if len(password) < 8:
            return HttpResponse('пароль слишком короткий')
        if password != password_test:
            return HttpResponse('пароли не совпадают')
        if not any(c.isupper() for c in password):
            return HttpResponse('пароль должен содержать заглавную букву')
        try:
            validate_email(email)
        except ValidationError:
            return HttpResponse('почта некорректна')

        user = User.objects.create_user(
            username=login,
            password=password,
            email=email,
        )
        if avatar:
            user.avatar = avatar
            user.save()

        auth_login(request, user)
        return HttpResponseRedirect('/users/')
    return render(request, 'users/index.html')

def users_auth(request):
    if request.method == 'POST':
        login = request.POST.get('login')
        password = request.POST.get('password')

        user = authenticate(request, username=login, password=password)
        if user:
            auth_login(request, user)
            return HttpResponseRedirect('/users/')

    return HttpResponseRedirect('/')

def users_logout(request):
    auth_logout(request)
    return HttpResponseRedirect('/')

def get_user_by_id(request, user_id):
    user = User.objects.filter(id=user_id).first()
    if user:
        return JsonResponse({'result': user.username})
    return JsonResponse({'result': None})
def is_authorized(request):
    if request.user.is_authenticated:
        return request.user
    return None