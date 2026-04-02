from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from .models import User, EmailVerification
import random
from django.utils import timezone


class AuthService:

    @staticmethod
    def get_tokens(user) -> dict:
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

    @staticmethod
    def logout(refresh_token: str) -> bool:
        """Добавляет refresh токен в blacklist. Возвращает False если токен невалидный"""
        try:
            token = RefreshToken(refresh_token)  # type: ignore
            token.blacklist()
            return True
        except TokenError:
            return False


class UserService:

    @staticmethod
    def get_all():
        return User.objects.all()

    @staticmethod
    def update(user, validated_data) -> User:
        for field, value in validated_data.items():
            setattr(user, field, value)
        user.save()
        return user

    @staticmethod
    def delete(user) -> None:
        user.delete()

    @staticmethod
    def update_profile(request) -> User:
        """Валидация и обновление профиля"""
        from .serializers import UserSerializer
        serializer = UserSerializer(request.user, data=request.data, partial=True, context={'request': request})
        serializer.is_valid(raise_exception=True)
        return UserService.update(request.user, serializer.validated_data)
    
class VerificationService:

    @staticmethod
    def generate_code() -> str:
        return str(random.randint(100000, 999999))

    @staticmethod
    def create_or_update(user) -> str:
        """Создаёт или обновляет код верификации, возвращает код"""
        code = VerificationService.generate_code()
        EmailVerification.objects.update_or_create(
            user=user,
            defaults={'code': code, 'created_at': timezone.now()}
        )
        return code

    @staticmethod
    def verify(user_id: int, code: str) -> tuple[bool, str]:
        """Проверяет код. Возвращает (успех, сообщение об ошибке)"""
        try:
            verification = EmailVerification.objects.get(user_id=user_id)
        except EmailVerification.DoesNotExist:
            return False, 'Код не найден'

        if verification.is_expired():
            verification.delete()
            return False, 'Код истёк'

        if verification.code != code:
            return False, 'Неверный код'

        verification.user.is_verified = True
        verification.user.save()
        verification.delete()
        return True, ''