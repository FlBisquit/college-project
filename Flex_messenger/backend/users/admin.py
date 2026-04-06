from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = [
        'username', 'email', 'date_birth',
        'online_badge', 'last_seen',
        'is_staff', 'is_active',
        'verified_badge', 'created_at'
    ]
    list_filter = ['is_staff', 'is_active', 'is_superuser', 'is_verified']
    search_fields = ['username', 'email']
    ordering = ['-created_at']
    readonly_fields = ['id', 'created_at', 'last_seen']

    fieldsets = list(UserAdmin.fieldsets) + [
        ('Дополнительно', {
            'fields': ('date_birth', 'avatar', 'bio', 'timezone', 'is_verified')
        }),
        ('Активность', {
            'fields': ('last_seen',)
        }),
    ]

    add_fieldsets = list(UserAdmin.add_fieldsets) + [
        ('Дополнительно', {
            'fields': ('email', 'date_birth', 'avatar')
        }),
    ]

    def online_badge(self, obj):
        if obj.is_online:
            return format_html('<span style="color: {};">● {}</span>', 'green', 'Онлайн')
        return format_html('<span style="color: {};">● {}</span>', 'grey', 'Офлайн')

    online_badge.short_description = 'Статус'

    def verified_badge(self, obj):
        if obj.is_verified:
            return format_html('<span style="color: {};">● {}</span>', 'green', 'Подтверждён')
        return format_html('<span style="color: {};">● {}</span>', '#f87171', 'Не подтверждён')

    verified_badge.short_description = 'Email'