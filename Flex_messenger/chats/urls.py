from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from django.urls import path
from . import views

app_name = 'chats'

urlpatterns = [
    path('create/', views.create_chat, name='create_chat'),
    path('delete/<str:chat_id>/', views.delete_chat, name='delete_chat'),
    path('join/<str:chat_id>/', views.join_to_chat, name='join_to_chat'),
    path('invite/<str:chat_id>/', views.invite_to_chat, name='invite_to_chat'),
    path('get/<str:chat_id>/', views.get_chat, name='get_chat'),
    path('list/', views.get_chat_list, name='get_chat_list'),
    path('update/<str:chat_id>/', views.update_chat_data, name='update_chat_data'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)