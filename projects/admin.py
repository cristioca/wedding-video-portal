from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Project, ProjectModification, File, FileDownloadEvent


class UserAdmin(BaseUserAdmin):
    """Custom User admin"""
    list_display = ['username', 'email', 'role', 'is_staff', 'is_active']
    list_filter = BaseUserAdmin.list_filter + ('role',)
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('role',)}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Additional Info', {'fields': ('role',)}),
    )


class FileInline(admin.TabularInline):
    """Inline admin for files in project"""
    model = File
    extra = 0
    readonly_fields = ['created_at', 'size_bytes']


class ProjectModificationInline(admin.TabularInline):
    """Inline admin for project modifications"""
    model = ProjectModification
    extra = 0
    readonly_fields = ['created_at', 'created_by']


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    """Project admin configuration"""
    list_display = ['name', 'user', 'type', 'status', 'edit_status', 'event_date', 'created_at']
    list_filter = ['type', 'status', 'edit_status', 'is_archived', 'created_at']
    search_fields = ['name', 'user__username', 'user__email', 'city']
    date_hierarchy = 'event_date'
    inlines = [FileInline, ProjectModificationInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'user', 'type', 'status', 'edit_status', 'is_archived')
        }),
        ('Event Details', {
            'fields': ('event_date', 'city', 'title_video', 'civil_union_details')
        }),
        ('Event Schedule', {
            'fields': ('prep', 'church', 'session', 'restaurant', 'details_extra')
        }),
        ('Editing', {
            'fields': ('editing_preferences', 'notes')
        }),
        ('Notifications', {
            'fields': ('admin_notified_of_changes', 'last_client_notification_date', 'has_unsent_changes'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ProjectModification)
class ProjectModificationAdmin(admin.ModelAdmin):
    """Project modification admin"""
    list_display = ['project', 'field_name', 'status', 'created_by', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['project__name', 'field_name']
    readonly_fields = ['created_at', 'approved_at']


@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    """File admin"""
    list_display = ['display_name', 'project', 'uploaded_by', 'get_size_display', 'created_at']
    list_filter = ['created_at']
    search_fields = ['display_name', 'project__name']
    readonly_fields = ['size_bytes', 'created_at']


@admin.register(FileDownloadEvent)
class FileDownloadEventAdmin(admin.ModelAdmin):
    """File download event admin"""
    list_display = ['file', 'downloaded_by', 'success', 'created_at']
    list_filter = ['success', 'created_at']
    readonly_fields = ['created_at']


# Register custom User admin
admin.site.register(User, UserAdmin)
