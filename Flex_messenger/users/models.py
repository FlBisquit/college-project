from django.db.models import (
    Model, CharField, IntegerField, EmailField, ImageField
)
from uuid import uuid4
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    id = CharField(
        default=uuid4,
        primary_key=True,
        max_length=36
    )
    avatar = ImageField(upload_to='avatars/', default='avatars/def.jpg')
