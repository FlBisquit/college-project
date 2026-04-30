from django.urls import path
from . import views

app_name = 'chatting'

urlpatterns = [
    path('history/<str:room_name>/', views.message_history, name='message_history'),
]