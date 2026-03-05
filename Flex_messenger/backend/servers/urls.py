from django.urls import path
from .views import *

urlpatterns = [
    path('main/', chat_main, name='chat_main'),
    path('create/', create_chat, name='create_chat'),
    path('delete/<str:chat_id>/', delete_chat, name='delete_chat'),
    path('join/<str:chat_id>/', join_to_chat, name='join_chat'),
    path('get/<str:chat_id>/', get_chat, name='get_chat'),
    path('list/', get_chat_list, name='get_chat_list'),
]