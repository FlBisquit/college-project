import uuid
from django.db import models
from users.models import User


class Server(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='server_avatars/', blank=True, null=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_servers')
    members = models.ManyToManyField(User, through='ServerMember', related_name='servers')
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Сервер'
        verbose_name_plural = 'Серверы'
        ordering = ['-created_at']


class ServerMember(models.Model):
    """Участник сервера"""

    class Role(models.TextChoices):
        OWNER = 'owner', 'Владелец'
        ADMIN = 'admin', 'Администратор'
        MEMBER = 'member', 'Участник'

    server = models.ForeignKey(Server, on_delete=models.CASCADE, related_name='server_members')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='server_memberships')
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.MEMBER)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('server', 'user')
        verbose_name = 'Владелец сервера'
        verbose_name_plural = 'Владельцы серверов'

    def __str__(self):
        return f'{self.user.username} → {self.server.name} ({self.get_role_display()})'  # type: ignore[attr-defined]