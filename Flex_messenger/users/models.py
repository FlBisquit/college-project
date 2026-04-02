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
    login = CharField(max_length=32)
    password = CharField(max_length=32)
    password_test = CharField(max_length=32,default="")
    email = EmailField(max_length = 256)
    avatar = ImageField(upload_to='avatars/', default='avatars/def.jpg')





   
    

    
                
        
    