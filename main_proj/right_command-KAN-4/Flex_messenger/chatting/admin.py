'''from django.contrib import admin
from .models import Chat,
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

@admin.register(Chat)
class ChatAdmin(DjangoUserAdmin):
    model = Chat
    list_display = ("participants")
    
class SellerAdmin(admin.ModelAdmin):
    model = Seller
    list_display = ("user","rating","balance")'''