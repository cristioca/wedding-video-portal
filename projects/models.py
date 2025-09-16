from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class User(AbstractUser):
    """Custom User model with role field"""
    ROLE_CHOICES = [
        ('ADMIN', 'Admin'),
        ('CLIENT', 'Client'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='CLIENT')
    
    def is_admin(self):
        return self.role == 'ADMIN'
    
    def is_client(self):
        return self.role == 'CLIENT'


class Project(models.Model):
    """Wedding video project model"""
    PROJECT_TYPE_CHOICES = [
        ('NUNTA', 'Nunta'),
        ('BOTEZ', 'Botez'),
    ]
    
    STATUS_CHOICES = [
        ('Planning', 'Planning'),
        ('Filming', 'Filming'),
        ('Editing', 'Editing'),
        ('Completed', 'Completed'),
    ]
    
    EDIT_STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('In Progress', 'In Progress'),
        ('Review', 'Review'),
        ('Completed', 'Completed'),
    ]
    
    # Basic fields
    name = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='projects')
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Planning')
    edit_status = models.CharField(max_length=50, choices=EDIT_STATUS_CHOICES, default='Pending')
    notes = models.TextField(blank=True, null=True)
    is_archived = models.BooleanField(default=False)
    
    # Event details
    event_date = models.DateTimeField()
    type = models.CharField(max_length=10, choices=PROJECT_TYPE_CHOICES)
    title_video = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    civil_union_details = models.TextField(blank=True, null=True)
    prep = models.TextField(blank=True, null=True)
    church = models.TextField(blank=True, null=True)
    session = models.TextField(blank=True, null=True)
    restaurant = models.TextField(blank=True, null=True)
    details_extra = models.TextField(blank=True, null=True)
    editing_preferences = models.TextField(blank=True, null=True)
    
    # Notification tracking
    admin_notified_of_changes = models.BooleanField(default=False)
    last_client_notification_date = models.DateTimeField(blank=True, null=True)
    has_unsent_changes = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.user.username}"


class ProjectModification(models.Model):
    """Track field modifications with approval workflow"""
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('AUTO_APPLIED', 'Auto Applied'),
    ]
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='modifications')
    field_name = models.CharField(max_length=100)
    old_value = models.TextField(blank=True, null=True)
    new_value = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='modifications_created')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='modifications_approved')
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.project.name} - {self.field_name} - {self.status}"


class File(models.Model):
    """Uploaded files for projects"""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='files')
    display_name = models.CharField(max_length=255)
    file = models.FileField(upload_to='project_files/%Y/%m/%d/')
    size_bytes = models.BigIntegerField()
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.display_name} - {self.project.name}"
    
    def get_size_display(self):
        """Return human-readable file size"""
        size = self.size_bytes
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"


class FileDownloadEvent(models.Model):
    """Track file downloads"""
    file = models.ForeignKey(File, on_delete=models.CASCADE, related_name='downloads')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='downloads')
    downloaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    success = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Download: {self.file.display_name} at {self.created_at}"
