from django.contrib import admin
from django.urls import path

from users.views import (
    users_auth, users_index, users_register, users_main,get_user_by_id, registrate,authorize,is_authorized,change_user,change_name
)

app_name = 'users'


urlpatterns = [
    path('admin/', admin.site.urls),

    
    path('register/', registrate),
    path('authorize/', authorize),
    path('is_autharized/',is_authorized),
    path('', users_main),
    path('register/', users_register),
    path('auth/', users_auth),
    path('change/',change_user),
    path('change_name/',change_name),
    path('get/<str:user_id>/', get_user_by_id),
    
]