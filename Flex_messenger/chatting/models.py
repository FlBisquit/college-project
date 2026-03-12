from django.db.models import Model,CharField,JSONField,IntegerField,ForeignKey,BooleanField,TextField,DateTimeField,CASCADE               
from chats.models import Chat
from users.models import User     
                                                                                



class Message(Model):
    chat = ForeignKey(
        Chat,
        on_delete=CASCADE,
        related_name='messages'
    )
    user = ForeignKey(
        User,
        on_delete=CASCADE
    )
    text = TextField()
    created_at =DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.login}: {self.text[:20]}'