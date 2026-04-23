from rest_framework import status, views
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import login, logout
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_protect, csrf_exempt
from django.utils.decorators import method_decorator
from .models import User
from .serializers import UserSerializer, UserRegisterSerializer, UserAuthSerializer
from .services import UserService, VerificationService, IsVerified


@method_decorator(csrf_exempt, name='dispatch')
class RegisterView(views.APIView):
    """Регистрация нового пользователя"""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {
                "message": "Регистрация успешна",
                "user": UserSerializer(user).data,
                "user_id": user.id,
            },
            status=status.HTTP_201_CREATED,
        )


@method_decorator(csrf_exempt, name='dispatch')
class LoginView(views.APIView):
    """Аутентификация пользователя с помощью email и пароля"""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserAuthSerializer(data=request.data, context={'request': request})
        if not serializer.is_valid():
            return Response(
                {"message": "Неверный логин или пароль"},
                status=status.HTTP_401_UNAUTHORIZED
            )
        user = serializer.validated_data['user']

        if not user.is_verified:
            return Response(
                {"detail": "Email не подтверждён", "user_id": user.id, "email": user.email},
                status=status.HTTP_403_FORBIDDEN
            )

        login(request, user)
        return Response({
            "message": "Вход выполнен",
            "user": UserSerializer(user).data,
        })


@method_decorator(csrf_exempt, name='dispatch')
class LogoutView(views.APIView):
    """Выход пользователя"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response({"message": "Выход выполнен"})


class ProfileView(views.APIView):
    """Просмотр, обновление и удаление профиля текущего пользователя"""
    permission_classes = [IsAuthenticated, IsVerified]

    def get(self, request):
        if request.user.is_authenticated:
            print(f"Пользователь: {request.user.username}")
        serializer = UserSerializer(request.user, context={'request': request})
        return Response(serializer.data)

    def put(self, request):
        user = UserService.update_profile(request)
        return Response({
            "message": "Профиль обновлен",
            "user": UserSerializer(user, context={'request': request}).data
        })

    def patch(self, request):
        user = UserService.update_profile(request)
        return Response({
            "message": "Профиль обновлен",
            "user": UserSerializer(user, context={'request': request}).data
        })

    def delete(self, request):
        UserService.delete(request.user)
        return Response({"message": "Аккаунт удален"}, status=status.HTTP_204_NO_CONTENT)


class UserView(views.APIView):
    """Список всех пользователей и детали конкретного"""
    permission_classes = [IsAuthenticated, IsVerified]

    def get(self, request):
        pk = self.kwargs.get('pk')
        if pk is None:
            queryset = UserService.get_all()
            serializer = UserSerializer(queryset, many=True)
            return Response(serializer.data)
        else:
            try:
                user = User.objects.get(pk=pk)
            except User.DoesNotExist:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
            serializer = UserSerializer(user)
            return Response(serializer.data)


class VerifyEmailView(views.APIView):
    """Подтверждение email по коду"""
    permission_classes = [AllowAny]

    def post(self, request):
        user_id = request.data.get('user_id')
        code = request.data.get('code')

        if not user_id or not code:
            return Response(
                {'message': ''},
                status=status.HTTP_400_BAD_REQUEST
            )

        success, error = VerificationService.verify(user_id, code)
        if not success:
            return Response(
                {'message': error},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response({'message': 'Email подтверждён'})


@method_decorator(csrf_exempt, name='dispatch')
class ResendCodeView(views.APIView):
    """Повторная отправка кода верификации"""
    permission_classes = [AllowAny]

    def post(self, request):
        user_id = request.data.get('user_id')

        if not user_id:
            return Response(
                {'message': 'user_id обязателен'},
                status=status.HTTP_400_BAD_REQUEST
            )

        success, message = VerificationService.resend_code(user_id)
        if not success:
            return Response(
                {'message': message},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response({'message': message})