from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from .models import User, Profile


# ─────────────────────────────────────────────
# ПРОФИЛЬ
# ─────────────────────────────────────────────

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Автоматически создаёт профиль при регистрации"""
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Сохраняет профиль вместе с пользователем"""
    if hasattr(instance, 'profile'):
        instance.profile.save()


@receiver(pre_save, sender=Profile)
def delete_old_avatar(sender, instance, **kwargs):
    """Удаляет старый аватар при замене на новый"""
    if not instance.pk:
        return
    try:
        old = Profile.objects.get(pk=instance.pk)
        if old.avatar and old.avatar != instance.avatar:
            old.avatar.delete(save=False)
    except Profile.DoesNotExist:
        pass