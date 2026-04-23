from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
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
def on_user_saved(sender, instance, created, **kwargs):
    if created:
        if instance.is_superuser:
            instance.is_verified = True
            instance.save(update_fields=['is_verified'])
            return  # Email отправляется в view
