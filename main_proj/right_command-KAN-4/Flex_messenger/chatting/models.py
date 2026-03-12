from django.db.models import (
    Model, ManyToManyField,
    ForeignKey, TextField, DateTimeField,
    CASCADE, ImageField, UUIDField
)
import uuid
from django.contrib.auth.models import User

# Create your models here.

class Chat(Model):
     participants = ManyToManyField(User)
     uuid = UUIDField(default=uuid.uuid4, unique=True, editable=False)
     def __str__(self):
        return f"сhat {self.uuid}"
class Message(Model):

     chat = ForeignKey(Chat, on_delete=CASCADE, related_name="messages")
     author = ForeignKey(User,on_delete=CASCADE)
     text = TextField(blank=True)
     image = ImageField(upload_to='chat_images/')
     created_at = DateTimeField(auto_now_add=True)