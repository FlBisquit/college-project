from django.contrib import admin
from django.utils.html import format_html
from .models import Server, ServerMember


class ServerMemberInline(admin.TabularInline):
    model = ServerMember
    extra = 0
    readonly_fields = ['joined_at']
    fields = ['user', 'role', 'joined_at']


@admin.register(Server)
class ServerAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'members_count', 'created_at']
    search_fields = ['name', 'owner__username']
    readonly_fields = ['id', 'created_at']
    inlines = [ServerMemberInline]

    def members_count(self, obj):
        return obj.server_members.count()
    members_count.short_description = 'Участников'


@admin.register(ServerMember)
class ServerMemberAdmin(admin.ModelAdmin):
    list_display = ['user', 'server', 'role', 'joined_at']
    list_filter = ['role']
    search_fields = ['user__username', 'server__name']
    readonly_fields = ['joined_at']