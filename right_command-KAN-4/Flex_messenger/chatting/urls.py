from django.urls import path
from . import views

urlpatterns = [
    path('<uuid:room_name>/', views.room, name='room')
]