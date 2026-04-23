from django.urls import path
from .views import RegisterView, LoginView, LogoutView, ProfileView, UserView, VerifyEmailView, ResendCodeView

app_name = 'users'

urlpatterns = [
    # Auth
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    # Profile
    path('profile/', ProfileView.as_view(), name='profile'),
    # Email
    path('verify-email/', VerifyEmailView.as_view(), name='verify-email'),
    path('resend-code/', ResendCodeView.as_view(), name='resend-code'),
    # Users
    path('', UserView.as_view(), name='user-list'),
    path('<int:pk>/', UserView.as_view(), name='user-detail'),
]