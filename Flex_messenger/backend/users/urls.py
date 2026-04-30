from django.urls import path, include
from . import views

auth_patterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('verify-email/', views.VerifyEmailView.as_view(), name='verify-email'),
    path('resend-code/', views.ResendCodeView.as_view(), name='resend-code'),
]

user_patterns = [
    path('', views.UserListView.as_view(), name='user-list'),
    path('<int:user_id>/', views.UserDetailView.as_view(), name='user-detail'),
]

urlpatterns = [
    path('auth/', include(auth_patterns)),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('users/', include(user_patterns)),
]