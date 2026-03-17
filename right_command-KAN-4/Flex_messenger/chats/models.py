from django.db.models import Model,CharField,JSONField,IntegerField,ForeignKey,BooleanField,TextField,CASCADE, UUIDField
from uuid import uuid4
from users.models import User

def generate_uuid():
    return str(uuid4())
def unic_number():
    from random import randint
    return f"{randint(0, 999999):06d}"


class Chat(Model):
    id = UUIDField(primary_key=True, default=uuid4, editable=False)
    number = CharField(max_length=6,default=unic_number)
    owner = ForeignKey(User,on_delete=CASCADE)
    max_chaters = IntegerField(default=12)
    done = BooleanField(default=False)
    started = BooleanField(default=False)
    chatName = CharField(max_length=150, default='test_chat')
    
class ChatData(Model):
    owner = ForeignKey(Chat, on_delete=CASCADE)
    user = ForeignKey(User, on_delete=CASCADE)
    data = JSONField(default=dict)
