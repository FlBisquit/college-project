from django.urls import path
from . import views

app_name = 'servers'

urlpatterns = [
    path('', views.ServerListCreateView.as_view(), name='list'),
    path('<uuid:pk>/', views.ServerDetailView.as_view(), name='detail'),
    path('<uuid:pk>/join/', views.JoinServerView.as_view(), name='join'),
    path('<uuid:pk>/leave/', views.LeaveServerView.as_view(), name='leave'),
    path('<uuid:pk>/members/', views.ServerMembersView.as_view(), name='members'),
    path('<uuid:pk>/members/<int:user_id>/role/', views.UpdateMemberRoleView.as_view(), name='member-role'),
]