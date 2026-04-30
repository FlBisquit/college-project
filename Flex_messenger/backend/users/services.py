import logging
import os
import random

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone
from rest_framework.permissions import BasePermission
from rest_framework.throttling import UserRateThrottle

from .models import User, EmailVerification

logger = logging.getLogger(__name__)


# ============================================================================
# RATE LIMITING CLASSES
# ============================================================================

class ResendCodeThrottle(UserRateThrottle):
    """
    Ограничение на переотправку кода верификации.
    3 попытки в час для защиты от spam.
    """
    scope = 'resend_code'
    rate = '3/h'


# ============================================================================
# PERMISSION CLASSES
# ============================================================================

class IsVerified(BasePermission):
    """
    Проверяет, что пользователь подтвердил email.
    Используется как permission_class в views.
    """
    message = "Необходимо подтвердить email для доступа к этому ресурсу"

    def has_permission(self, request, view):
        """Check if user is authenticated and email verified"""
        if not request.user or not request.user.is_authenticated:
            return False
        
        if not request.user.is_verified:
            logger.warning(
                f"Unverified user {request.user.id} ({request.user.email}) "
                f"tried to access {view.__class__.__name__}"
            )
            return False
        
        return True


# ============================================================================
# USER SERVICE
# ============================================================================

class UserService:
    """
    Сервис для управления пользователями.
    Инкапсулирует бизнес-логику работы с User.
    """

    @staticmethod
    def get_all():
        """Получить всех пользователей"""
        return User.objects.all()

    @staticmethod
    def update(user: User, validated_data: dict) -> User:
        """
        Обновить пользователя с валидацией защищённых полей.
        
        Args:
            user: User instance to update
            validated_data: Validated data from serializer
        
        Returns:
            Updated User instance
        """
        # Поля которые запрещено менять через API
        protected_fields = {
            'id',
            'password',  # Используй специальное изменение пароля
            'is_staff',
            'is_superuser',
            'is_verified',
            'created_at',
            'updated_at',
        }
        
        updated_fields = []
        
        for field, value in validated_data.items():
            if field in protected_fields:
                logger.warning(
                    f"Attempt to update protected field '{field}' for user {user.id}"
                )
                continue
            
            if hasattr(user, field):
                setattr(user, field, value)
                updated_fields.append(field)
        
        user.save()
        logger.info(f"User {user.id} updated fields: {', '.join(updated_fields)}")
        return user

    @staticmethod
    def update_profile(request) -> User:
        """
        Обновить профиль пользователя через API.
        Обрабатывает загрузку аватара и удаление старого файла.
        
        Args:
            request: Django request object with user and data
        
        Returns:
            Updated User instance
        
        Raises:
            ValidationError: If serializer validation fails
        """
        from .serializers import UserSerializer
        
        # Сохранить старый аватар для удаления
        old_avatar = request.user.avatar
        
        # Валидировать и получить новые данные
        serializer = UserSerializer(
            request.user,
            data=request.data,
            partial=True,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        
        # Если аватар изменился — удалить старый файл
        if 'avatar' in request.data and old_avatar:
            try:
                avatar_path = old_avatar.path
                if os.path.exists(avatar_path):
                    os.remove(avatar_path)
                    logger.info(f"Deleted old avatar for user {request.user.id}: {avatar_path}")
            except Exception as e:
                logger.error(f"Error deleting old avatar for user {request.user.id}: {e}")
        
        # Обновить пользователя
        return UserService.update(request.user, serializer.validated_data) # type: ignore

    @staticmethod
    def delete(user: User) -> None:
        """
        Удалить пользователя.
        Логирует критическое действие.
        
        Args:
            user: User instance to delete
        """
        user_id = user.id
        username = user.username
        email = user.email
        
        user.delete()
        logger.warning(
            f"User deleted: id={user_id}, username={username}, email={email}"
        )


# ============================================================================
# EMAIL VERIFICATION SERVICE
# ============================================================================

class VerificationService:
    """
    Сервис для управления email верификацией.
    Генерирует коды, отправляет письма, проверяет коды.
    """

    @staticmethod
    def generate_code() -> str:
        """Генерировать 6-значный код верификации"""
        return str(random.randint(100000, 999999))

    @staticmethod
    def send_verification_email(user: User, code: str) -> bool:
        """
        Отправить письмо с кодом верификации.
        
        Args:
            user: User instance
            code: Verification code (6 digits)
        
        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            # Рендерить HTML шаблон
            html = render_to_string('users/email_verification.html', {
                'username': user.username,
                'code': code,
            })
            
            # Создать письмо
            msg = EmailMultiAlternatives(
                subject='Подтверждение email',
                body='Используйте код для подтверждения email',  # Fallback plain text
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email]
            )
            msg.attach_alternative(html, 'text/html')
            msg.send()
            
            logger.info(f"Verification email sent to {user.email}")
            return True
        
        except Exception as e:
            logger.error(
                f"Error sending verification email to {user.email}: {e}",
                exc_info=True
            )
            return False

    @staticmethod
    def create_or_update(user: User) -> str:
        """
        Создать или обновить код верификации.
        Не отправляет письмо — это должно делаться отдельно через Celery.

        Args:
            user: User instance

        Returns:
            Generated verification code

        Raises:
            ValueError: If user email already verified
        """
        if user.is_verified:
            raise ValueError("User email already verified")

        # Сгенерировать код
        code = VerificationService.generate_code()

        # Создать или обновить запись верификации
        EmailVerification.objects.update_or_create(
            user=user,
            defaults={
                'code': code,
                'created_at': timezone.now(),
                'attempts': 0,  # Reset attempts
            }
        )

        logger.info(f"Verification code generated for user {user.id}")
        return code

    @staticmethod
    def resend_code(user_id: str) -> tuple[bool, str]:
        """
        Повторная отправка кода верификации.
        """
        logger.warning(f"Resend code for user {user_id}")
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            logger.warning(f"Resend code requested for non-existent user: {user_id}")
            return False, 'Пользователь не найден'

        if user.is_verified:
            logger.info(f"Resend code requested for already verified user: {user_id}")
            return False, 'Email уже подтверждён'

        try:
            code = VerificationService.create_or_update(user)
            from .tasks import send_verification_email
            send_verification_email.delay(user.id, code)
            logger.info(f"Verification code resent to {user.email}")
            return True, f'Код отправлен на {user.email}'

        except Exception as e:
            logger.error(f"Error resending code to {user.email}: {e}", exc_info=True)
            return False, f'Ошибка отправки email: {str(e)}'

    @staticmethod
    def verify(user_id: str, code: str) -> tuple[bool, str]:
        """
        Проверить код верификации и подтвердить email пользователя.
        Использует select_for_update() для защиты от race conditions.

        Args:
            user_id: User ID
            code: Verification code

        Returns:
            (success: bool, message: str)
        """

        logger.warning(f"Verifying code for user {user_id}: input '{code}'")
        try:
            # select_for_update() лочит запись — защита от race condition
            verification = EmailVerification.objects.select_for_update().get(
                user_id=user_id
            )
        except EmailVerification.DoesNotExist:
            logger.warning(f"Verify code requested for non-existent verification: {user_id}")
            return False, 'Код не найден'
        logger.warning(f"Stored code: '{verification.code}', attempts: {verification.attempts}, expired: {verification.is_expired()}")

        # Проверить срок действия кода
        if verification.is_expired():
            verification.delete()
            logger.info(f"Verification code expired for user {user_id}")
            return False, 'Код истёк'

        if code != verification.code:
            logger.warning(
                f"Invalid verification code for user {user_id}. "
                f"Input: '{code}', Stored: '{verification.code}'"
            )
            return False, 'Неверный код'

        # Подтвердить email пользователя
        user = verification.user
        user.is_verified = True
        user.save()
        verification.delete()
        
        logger.info(f"User {user_id} email verified successfully")
        return True, 'Email успешно подтверждён'