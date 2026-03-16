from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone as tz

def avatar_upload_path(instance, filename):
    """Функция обработки названий аватаров пользователей (под их названия логина)"""
    ext = filename.split('.')[-1]
    return f'avatars/{instance.username}.{ext}'

class User(AbstractUser):
    """Кастомная модель пользователя"""
    email = models.EmailField(unique=True)
    bio = models.TextField(max_length=500, blank=True, default='')
    date_birth = models.DateField(null=True, blank=True)
    avatar = models.ImageField(upload_to=avatar_upload_path, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField(null=True, blank=True)
    is_banned = models.BooleanField(default=False)
    timezone = models.CharField(max_length=50, default='UTC')

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    @property
    def is_online(self):
        if not self.last_seen:
            return False
        return (tz.now() - self.last_seen).seconds < 60

    @property
    def online_status(self):
        if self.is_online:
            return 'online'
        if not self.last_seen:
            return 'offline'
        delta = tz.now() - self.last_seen
        if delta.seconds < 60:
            return 'recently'
        return 'offline'

    @property
    def last_seen_display(self):
        if not self.last_seen:
            return 'Никогда'
        delta = tz.now() - self.last_seen
        if delta.seconds < 60:
            return 'Только что'
        if delta.seconds < 3600:
            return f'{delta.seconds // 60} мин. назад'
        if delta.days == 0:
            return f'{delta.seconds // 3600} ч. назад'
        if delta.days == 1:
            return 'Вчера'
        return self.last_seen.strftime('%d.%m.%Y')

    def avatar_url(self):
        if self.avatar:
            return self.avatar.url
        return '/static/images/default_avatar.png'

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'