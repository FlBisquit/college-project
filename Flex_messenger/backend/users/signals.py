# Global
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.core.mail import send_mail
# Local
from .models import User


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
    """Отправляет письмо при регистрации"""
    if created:
        send_mail(
            subject='Добро пожаловать!',
            message=f'Привет, {instance.username}! Спасибо за регистрацию.',
            from_email=None,
            recipient_list=[instance.email],
            fail_silently=False,
        )