from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from .views import (
    ChatListApiView,
    CreateChatApiView,
    DeleteChatAPIView,
    JoinToChatAPIView,
    InviteToChatAPIView,
    GetChatAPIView,
    UpdateChatDataAPIView
)

app_name = 'chats'

urlpatterns = [
    path('list/', ChatListApiView.as_view(), name='chat_list'),
    path('create/', CreateChatApiView.as_view(), name='create_chat'),
    path('delete/<str:chat_id>/', DeleteChatAPIView.as_view(), name='delete_chat'),
    path('join/<str:chat_id>/', JoinToChatAPIView.as_view(), name='join_to_chat'),
    path('invite/<str:chat_id>/', InviteToChatAPIView.as_view(), name='invite_to_chat'),
    path('get/<str:chat_id>/', GetChatAPIView.as_view(), name='get_chat'),
    path('update/<str:chat_id>/', UpdateChatDataAPIView.as_view(), name='update_chat_data'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)