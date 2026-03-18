from django.urls import path
from . import views

app_name = 'chatting'

urlpatterns = [
    path('room/<str:chat_id>/', views.room, name='room'),
]