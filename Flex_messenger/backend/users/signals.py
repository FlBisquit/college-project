# Global
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.core.mail import send_mail
# Local
from .models import User, EmailVerification
from .services import VerificationService

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
def send_welcome_email(sender, instance, created, **kwargs):
    if created:
        if instance.is_superuser:
            instance.is_verified = True
            instance.save(update_fields=['is_verified'])
            return

        code = VerificationService.create_or_update(instance)
        send_mail(
            subject='Подтверждение регистрации — Flex Messenger',
            message=f'Привет, {instance.username}!\n\nТвой код подтверждения: {code}\n\nКод действителен 10 минут.',
            from_email=None,
            recipient_list=[instance.email],
            fail_silently=False,
        )