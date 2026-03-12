from django.shortcuts import render,HttpResponseRedirect
from .models import User
from chats.models import Chat
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

def user_profile(request):
    if user := is_authorized(request):
        user = is_authorized(request)
        
        if not user:
            return HttpResponseRedirect("/")
        
        login = user.login
        avatar = user.avatar
        hidden_password = "*" * len(user.password)
        print(avatar)
        email = user.email 


        return render(request, "users/profile.html", context={
            "user": user,
            "login": login,
            "hidden_password": hidden_password,
            "email": email,
            "avatar": avatar,
        })
    return HttpResponseRedirect('/')
    



def change_user(request):
    
    return render(request, 'users/change.html')

def change_name(request):
    if request.method == "POST":
        old_login = request.POST.get("old_login")
        password = request.POST.get("password")
        new_login = request.POST.get("new_login")

        user = User.objects.filter(login=old_login, password=password).first()
        if not user:
            return HttpResponse("Неверный ник или пароль")

        if User.objects.filter(login=new_login).exists():
            return HttpResponseRedirect('/users/')

        user.login = new_login
        user.save()

        return HttpResponseRedirect("/users/")
    
def change_password(request):
    if request.method == "POST":
        old_password = request.POST.get("old_password")
        new_password = request.POST.get("new_password")

        user = User.objects.filter(password=old_password).first()
        if not user:
            return HttpResponse("Неверный пароль")

        if User.objects.filter(password=new_password).exists():
            return HttpResponseRedirect('/users/')

        user.password = new_password
        user.save()

        return HttpResponseRedirect("/users/")

def change_avatar(request):
    if request.method == "POST":
        password = request.POST.get("password")
        new_avatar = request.FILES['avatar']

        user = User.objects.filter(password=password).first()
        if not user:
            return HttpResponse("Неверный пароль")

        if User.objects.filter(avatar=new_avatar).exists():
            return HttpResponseRedirect('/users/')

        user.avatar = new_avatar
        user.save()

        return HttpResponseRedirect("/users/")
    
    

def users_index(request):
    
    return render(request, 'users/index.html')

def users_main(request):
    if user := is_authorized(request):
        chats = Chat.objects.all()
        return render(request, 'users/users.html', context={
            'user': user,
            'chats': chats,
            
        })
    return HttpResponseRedirect('/')

def registrate(request):
    if request.method == 'POST':
        login = request.POST.get('login')
        password = request.POST.get('password')
        password_test = request.POST.get('password2')
        email = request.POST.get('email')
        avatar = request.FILES['avatar']

        if User.objects.filter(login=login).exists():
            return HttpResponse("Пользователь уже существует")

        if len(password) < 8:
            return HttpResponse("Пароль слишком короткий")

        if password != password_test:
            return HttpResponse("Пароли не совпадают")
        
        if password.istitle() == False:
            return HttpResponse('Пароль не содержит заглавную букву')
        try: validate_email(email)
        except ValidationError:
            return HttpResponse('Почта не коректна')
            

        user = User.objects.create(
            login=login,
            password=password,
            email = email,
            avatar = avatar,
        )

        authorize(request, login, password)
        return HttpResponseRedirect('/users/')
    return render(request, 'users/index.html')
            
def authorize( request, login, password):
        if user := User.objects.filter(
            login=login,
            password=password
        ).first():
            request.session['user_id'] = str(user.id)
            request.session['login'] = user.login
            return user
        
def is_authorized(request):
        if user_id := request.session.get('user_id'):
            return User.objects.get(id=user_id)

def users_auth(request):
    login = request.POST.get('login')
    password =request.POST.get('password')
    if authorize(request, login, password):
        return HttpResponseRedirect('/users/')
    return HttpResponseRedirect('/')

def users_register(request):
    login = request.POST.get('login')
    password = request.POST.get('password')
    email = request.POST.get('email')
    avatar = request.POST.get('avatar')

    if registrate(request, login, password, email, avatar):
        return HttpResponseRedirect('/users/')
    return HttpResponseRedirect('/')

def get_user_by_id(request, user_id):
    user = User.objects.filter(id=user_id).first()
    if user:
        return JsonResponse({'result': user.login})
    return JsonResponse({'result': None})
