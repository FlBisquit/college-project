from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from .models import User


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
            token = RefreshToken(refresh_token)
            token.blacklist()
            return True
        except (TokenError, Exception):
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