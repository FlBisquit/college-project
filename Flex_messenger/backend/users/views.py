from rest_framework import generics, viewsets, mixins, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import UserSerializer, UserRegisterSerializer, UserAuthSerializer
from .services import AuthService, UserService


class RegisterView(generics.CreateAPIView):
    """Регистрация нового пользователя"""
    permission_classes = [AllowAny]
    serializer_class = UserRegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {
                "message": "Регистрация успешна",
                "user": UserSerializer(user).data,
                "tokens": AuthService.get_tokens(user)
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(generics.GenericAPIView):
    """Аутентификация пользователя"""
    permission_classes = [AllowAny]
    serializer_class = UserAuthSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        if not serializer.is_valid():
            return Response(
                {"detail": "Неверный логин или пароль"},
                status=status.HTTP_401_UNAUTHORIZED
            )
        user = serializer.validated_data['user']
        return Response({
            "message": "Вход выполнен",
            "user": UserSerializer(user).data,
            "tokens": AuthService.get_tokens(user)
        })


class LogoutView(generics.GenericAPIView):
    """Выход пользователя"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response(
                {"detail": "Refresh токен обязателен"},
                status=status.HTTP_400_BAD_REQUEST
            )
        success = AuthService.logout(refresh_token)
        if not success:
            return Response(
                {"detail": "Недействительный токен"},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response({"message": "Выход выполнен"})


class ProfileView(generics.RetrieveUpdateDestroyAPIView):
    """Просмотр, обновление и удаление профиля текущего пользователя"""
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        user = UserService.update_profile(request)
        return Response({
            "message": "Профиль обновлен",
            "user": UserSerializer(user, context={'request': request}).data
        })

    def destroy(self, request, *args, **kwargs):
        UserService.delete(request.user)
        return Response({"message": "Аккаунт удален"}, status=status.HTTP_204_NO_CONTENT)


class UserViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """Список всех пользователей и детали конкретного"""
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_queryset(self):
        return UserService.get_all()