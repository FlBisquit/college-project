from django.db.models import (
    Model, ManyToManyField,
    ForeignKey, TextField, DateTimeField,
    CASCADE
)

from django.contrib.auth.models import User

# Create your models here.

class Chat(Model):
     participants = ManyToManyField(User)

class Message(Model):
     chat = ForeignKey(Chat, on_delete=CASCADE, related_name="messages")
     author = ForeignKey(User,on_delete=CASCADE)
     text = TextField()
     created_at = DateTimeField(auto_now_add=True)