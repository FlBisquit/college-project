from rest_framework import status, views
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated

from django.contrib.auth import login, logout
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from django.utils.decorators import method_decorator

from .models import User
from .serializers import UserSerializer, UserRegisterSerializer, UserAuthSerializer
from .services import UserService, VerificationService, IsVerified, VerifyEmailThrottle, ResendCodeThrottle
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# AUTHENTICATION VIEWS
# ============================================================================

@method_decorator(csrf_exempt, name='dispatch')
class RegisterView(views.APIView):
    """Регистрация нового пользователя"""
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Создать новый аккаунт.
        POST защищён CSRF middleware автоматически.
        ensure_csrf_cookie гарантирует токен в cookie для фронтенда.
        """
        serializer = UserRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Отправка email асинхронно
        if user.is_superuser: # type: ignore
            # Для superuser подтверждение не требуется, email не отправляется
            pass
        else:
            from .services import VerificationService
            from .tasks import send_verification_email
            code = VerificationService.create_or_update(user) # type: ignore
            send_verification_email.delay(user.id, code) # type: ignore

        return Response(
            {
                "message": "Регистрация успешна",
                "user": UserSerializer(user).data,
                "user_id": user.id, # type: ignore
            },
            status=status.HTTP_201_CREATED,
        )


@method_decorator(csrf_exempt, name='dispatch')
class LoginView(views.APIView):
    """Аутентификация пользователя с помощью email и пароля"""
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Вход в аккаунт.
        POST защищён CSRF middleware.
        Требует email подтверждение перед входом.
        """
        serializer = UserAuthSerializer(data=request.data, context={'request': request})
        if not serializer.is_valid():
            return Response(
                {"message": "Неверный логин или пароль"},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        user = serializer.validated_data['user'] # type: ignore

        if not user.is_verified:
            logger.warning(f"Login failed for user {user.id} (pk: {user.pk}): not verified, returning user_id={str(user.pk)}, email={user.email}")
            return Response(
                {
                    "detail": "Email не подтверждён",
                    "user_id": str(user.pk),
                    "email": user.email
                },
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
        """
        Выход из аккаунта.
        CSRF защита включена по умолчанию для POST.
        """
        logout(request)
        return Response({"message": "Выход выполнен"})


# ============================================================================
# PROFILE VIEWS
# ============================================================================

@method_decorator(ensure_csrf_cookie, name='dispatch')
class ProfileView(views.APIView):
    """Просмотр, обновление и удаление профиля текущего пользователя"""
    permission_classes = [IsAuthenticated, IsVerified]

    def get(self, request):
        """Получить профиль текущего пользователя"""
        logger.debug(f"Profile accessed by user: {request.user.username}")
        serializer = UserSerializer(request.user, context={'request': request})
        return Response(serializer.data)

    def put(self, request):
        """Полное обновление профиля (все поля)"""
        user = UserService.update_profile(request)
        return Response({
            "message": "Профиль обновлен",
            "user": UserSerializer(user, context={'request': request}).data
        })

    def patch(self, request):
        """Частичное обновление профиля"""
        user = UserService.update_profile(request)
        return Response({
            "message": "Профиль обновлен",
            "user": UserSerializer(user, context={'request': request}).data
        })

    def delete(self, request):
        """Удалить аккаунт пользователя"""
        UserService.delete(request.user)
        return Response(
            {"message": "Аккаунт удален"},
            status=status.HTTP_204_NO_CONTENT
        )


# ============================================================================
# USER LIST & DETAIL VIEWS
# ============================================================================

class UserListView(views.APIView):
    """Список всех пользователей"""
    permission_classes = [IsAuthenticated, IsVerified]

    def get(self, request):
        """Получить список всех пользователей"""
        queryset = UserService.get_all()
        serializer = UserSerializer(queryset, many=True, context={'request': request})
        return Response({
            "message": "Список пользователей",
            "data": serializer.data
        })


class UserDetailView(views.APIView):
    """Детали конкретного пользователя"""
    permission_classes = [IsAuthenticated, IsVerified]

    def get(self, request, user_id):
        """Получить данные конкретного пользователя"""
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response(
                {'error': 'Пользователь не найден'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = UserSerializer(user, context={'request': request})
        return Response({
            "message": "Данные пользователя",
            "data": serializer.data
        })


# ============================================================================
# EMAIL VERIFICATION VIEWS
# ============================================================================

@method_decorator(csrf_exempt, name='dispatch')
class VerifyEmailView(views.APIView):
    """Подтверждение email по коду верификации"""
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Подтвердить email код.
        Rate limit: 5 попыток в час.
        """
        user_id = request.data.get('user_id')
        code = request.data.get('code')
        logger.warning(f"Verify request: user_id='{user_id}', code='{code}'")

        if not user_id or not code:
            return Response(
                {'message': 'user_id и code обязательны'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Проверить существование пользователя
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response(
                {'message': 'Пользователь не найден'},
                status=status.HTTP_404_NOT_FOUND
            )

        success, error = VerificationService.verify(user_id, code)
        if not success:
            return Response({'message': error}, status=status.HTTP_400_BAD_REQUEST)

        user.refresh_from_db()
        login(request, user)

        return Response({
            'message': 'Email подтверждён',
            'user': UserSerializer(user, context={'request': request}).data
        })


@method_decorator(csrf_exempt, name='dispatch')
class ResendCodeView(views.APIView):
    """Повторная отправка кода верификации"""
    permission_classes = [AllowAny]
    throttle_classes = [ResendCodeThrottle]  # Защита от spam

    def post(self, request):
        """
        Переотправить код верификации.
        Rate limit: 3 попытки в час.
        """
        user_id = request.data.get('user_id')

        if not user_id:
            return Response(
                {'message': 'user_id обязателен'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Проверить существование пользователя
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response(
                {'message': 'Пользователь не найден'},
                status=status.HTTP_404_NOT_FOUND
            )

        success, message = VerificationService.resend_code(user_id)
        if not success:
            return Response(
                {'message': message},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response({'message': message})