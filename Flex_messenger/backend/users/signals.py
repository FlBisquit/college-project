from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from .models import User


def send_html_email(subject, template, context, to_email):
    """Отправляет HTML письмо"""
    html = render_to_string(template, context)
    msg = EmailMultiAlternatives(subject=subject, body='', to=[to_email])
    msg.attach_alternative(html, 'text/html')
    msg.send()


@receiver(pre_save, sender=User)
def delete_old_avatar(sender, instance, **kwargs):
    """Удаляет старый аватар при замене на новый"""
    if not instance.pk:
        return
    try:
        old = User.objects.get(pk=instance.pk)
        if old.avatar and old.avatar != instance.avatar:
            old.avatar.delete(save=False)
    except User.DoesNotExist:
        pass


@receiver(post_save, sender=User)
def on_user_saved(sender, instance, created, **kwargs):
    if created:
        if instance.is_superuser:
            instance.is_verified = True
            instance.save(update_fields=['is_verified'])
            return

        # если обычный пользователь отправляем код верификации
        from .services import VerificationService
        code = VerificationService.create_or_update(instance)

        send_html_email(
            subject='Подтверждение регистрации — Flex Messenger',
            template='users/email_verification.html',
            context={'username': instance.username, 'code': code},
            to_email=instance.email,
        )

    else:
        # Пользователь только что подтвердил email — отправляем приветствие
        if _just_verified(instance):
            send_html_email(
                subject='Добро пожаловать в Flex Messenger! 🎉',
                template='users/email_welcome.html',
                context={'username': instance.username},
                to_email=instance.email,
            )


def _just_verified(instance):
    """Проверяет что is_verified только что стало True"""
    try:
        old = User.objects.get(pk=instance.pk)
        return not old.is_verified and instance.is_verified
    except User.DoesNotExist:
        return False