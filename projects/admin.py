from django.contrib import admin
from .models import Project, ProjectInvitation

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'priority', 'created_at', 'is_active']
    list_filter = ['priority', 'is_active', 'created_at']
    search_fields = ['name', 'description', 'owner__username']
    filter_horizontal = ['members']

@admin.register(ProjectInvitation)
class ProjectInvitationAdmin(admin.ModelAdmin):
    list_display = ['project', 'inviter', 'invitee', 'accepted', 'created_at']
    list_filter = ['accepted', 'created_at']
