from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from users.views import (
    users_auth, users_index, users_register, users_main,get_user_by_id, registrate,authorize,is_authorized,change_user,change_name,user_profile, change_avatar,change_password
)

app_name = 'users'
# , name='login'

urlpatterns = [
    path('admin/', admin.site.urls),

    
    path('register/', registrate),
    path('authorize/', authorize),
    path('is_autharized/',is_authorized),
    path('', users_main),
    path('auth/', users_auth),
    path('change/',change_user),
    path('change_name/',change_name),
    path('change_password/',change_password),
    path('change_avatar/',change_avatar),
    path('profile/', user_profile),

    
    path('get/<str:user_id>/', get_user_by_id),
    
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)