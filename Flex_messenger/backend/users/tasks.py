from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from .models import User, EmailVerification
import logging

logger = logging.getLogger(__name__)


@shared_task
def send_verification_email(user_id, code):
    """Асинхронная отправка email с кодом верификации"""
    try:
        user = User.objects.get(id=user_id)
        html = render_to_string('users/email_verification.html', {
            'username': user.username,
            'code': code
        })
        msg = EmailMultiAlternatives(
            subject='Подтверждение регистрации — Flex Messenger',
            body='',
            to=[user.email]
        )
        msg.attach_alternative(html, 'text/html')
        msg.send()
        logger.info(f"Verification email sent to {user.email}")
    except User.DoesNotExist:
        logger.warning(f"User {user_id} does not exist, skipping email send")
    except Exception as e:
        logger.error(f"Failed to send verification email to user {user_id}: {e}")


@shared_task
def delete_expired_unverified_users():
    """Удаление пользователей, не подтвердивших email в течение 10 минут"""
    from django.utils import timezone
    # Найти пользователей, которые не подтвердили email и зарегистрировались более 10 минут назад
    expired_users = User.objects.filter(
        is_verified=False,
        date_joined__lt=timezone.now() - timezone.timedelta(minutes=10)
    )
    deleted_count = expired_users.count()
    expired_users.delete()
    logger.info(f"Deleted {deleted_count} expired unverified users")