from django.db import models
from django.conf import settings
from servers.models import Server


class Message(models.Model):
    server = models.ForeignKey(
        Server,
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name='Сервер'
    )

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name='Автор'
    )

    text = models.TextField(
        blank=True,
        verbose_name='Текст сообщения'
    )

    image = models.ImageField(
        upload_to='chat_images/',
        blank=True,
        null=True,
        verbose_name='Изображение'
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата и время отправки'
    )

    class Meta:
        ordering = ['created_at']
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'

    def __str__(self):
        if self.text:
            return f'{self.author}: {self.text[:20]}...'
        if self.image:
            return f'{self.author}: [Изображение]'
        return f'{self.author}: [Пустое сообщение]'