from django.urls import path
from . import views

app_name = 'servers'

urlpatterns = [
    # Основные CRUD операции
    path('', views.ServerListCreateView.as_view(), name='list'),
    path('my_servers/', views.MyServersView.as_view(), name='my-servers'),
    path('public_servers/', views.PublicServersView.as_view(), name='public-servers'),
    path('<uuid:pk>/', views.ServerDetailView.as_view(), name='detail'),
    
    # Вступление / выход
    path('<uuid:pk>/join/', views.JoinServerView.as_view(), name='join'),
    path('<uuid:pk>/leave/', views.LeaveServerView.as_view(), name='leave'),
    
    # Члены сервера
    path('<uuid:pk>/members/', views.ServerMembersView.as_view(), name='members'),
    path('<uuid:pk>/members/<uuid:user_id>/role/', views.UpdateMemberRoleView.as_view(), name='member-role'),
]