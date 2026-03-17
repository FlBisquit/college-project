from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from users.views import (
    users_auth, users_index, users_register, users_main,
    get_user_by_id, registrate,authorize,is_authorized,change_user
)
from .views import (
    create_chat, delete_chat, join_to_chat, chat_main,
    get_chat, get_chat_list, update_chat_data, chating_main
    
)
app_name = 'chats'
urlpatterns = [
    path('admin/', admin.site.urls),
    
    path('create/', create_chat),
    path('delete/<str:chat_id>/', delete_chat),
    path('join/<str:chat_id>/', join_to_chat),
    path('', chat_main),
    path('get/<str:chat_id>/', get_chat),
    path('list/', get_chat_list),
    path('chating/', chating_main)
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)