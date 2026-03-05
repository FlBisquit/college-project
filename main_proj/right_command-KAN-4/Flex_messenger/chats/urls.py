from django.urls import path
from .views import (
    create_chat, delete_chat, join_to_chat, chat_main,
    get_chat, get_chat_list, update_chat_data, chating_main
)

app_name = 'chats'

urlpatterns = [
    path('create/', create_chat),
    path('delete/<str:chat_id>/', delete_chat),
    path('join/<str:chat_id>/', join_to_chat),
    path('', chating_main), 
    path('get/<str:chat_id>/', get_chat),
    path('list/', get_chat_list),
]