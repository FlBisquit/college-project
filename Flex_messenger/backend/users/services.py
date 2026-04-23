from rest_framework.permissions import BasePermission
from .models import User, EmailVerification
import random
from django.utils import timezone
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings


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
        # Send email with code
        try:
            html = render_to_string('users/email_verification.html', {
                'username': user.username,
                'code': code,
            })
            msg = EmailMultiAlternatives(
                subject='Подтверждение email',
                body='',
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email]
            )
            msg.attach_alternative(html, 'text/html')
            msg.send()
        except Exception as e:
            print(f'Error sending email to {user.email}: {e}')
        return code

    @staticmethod
    def resend_code(user_id: str) -> tuple[bool, str]:
        """Повторно отправляет код верификации"""
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return False, 'Пользователь не найден'

        if user.is_verified:
            return False, 'Email уже подтверждён'

        try:
            code = VerificationService.create_or_update(user)
            return True, f'Код отправлен на {user.email}'
        except Exception as e:
            return False, f'Ошибка отправки email: {str(e)}'

    @staticmethod
    def verify(user_id: str, code: str) -> tuple[bool, str]:
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


class IsVerified(BasePermission):
    """
    Проверяет, что пользователь подтвердил email
    """
    message = "Необходимо подтвердить email для доступа к этому ресурсу"

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.is_verified