from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.utils.text import slugify
import re


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
    slug = models.SlugField(max_length=255, unique=True, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='projects')
    client_name = models.CharField(max_length=255, blank=True, null=True)
    client_email = models.EmailField(blank=True, null=True)
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
    
    # Field ordering configuration
    ceremony_field_order = models.JSONField(
        default=dict,
        blank=True,
        help_text="Custom order for ceremony detail fields"
    )
    
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
    
    def generate_slug(self):
        """Generate unique slug based on event date, type, and creation time"""
        # Format: 2026-05-29-nunta(20250915-t-093405)
        event_date_str = self.event_date.strftime('%Y-%m-%d')
        creation_date_str = self.created_at.strftime('%Y%m%d-t-%H%M%S')
        
        # Convert type to lowercase and handle Romanian characters
        type_slug = self.type.lower()
        
        # Create the slug
        slug_base = f"{event_date_str}-{type_slug}({creation_date_str})"
        
        # Ensure uniqueness by adding a counter if needed
        slug = slug_base
        counter = 1
        while Project.objects.filter(slug=slug).exclude(pk=self.pk).exists():
            slug = f"{slug_base}-{counter}"
            counter += 1
        
        return slug
    
    def save(self, *args, **kwargs):
        """Override save to generate slug if not provided"""
        if not self.slug:
            # Need to save first to get created_at timestamp
            if not self.pk:
                super().save(*args, **kwargs)
            self.slug = self.generate_slug()
            # Save again with the slug
            super().save(update_fields=['slug'])
        else:
            super().save(*args, **kwargs)
    
    def get_ceremony_fields_ordered(self):
        """Return ceremony fields in custom order"""
        default_order = [
            {'field': 'civil_union_details', 'label': 'Civil Union Details', 'rows': 3},
            {'field': 'prep', 'label': 'Preparation', 'rows': 2},
            {'field': 'church', 'label': 'Church', 'rows': 2},
            {'field': 'session', 'label': 'Photo Session', 'rows': 2},
            {'field': 'restaurant', 'label': 'Restaurant', 'rows': 2}
        ]
        
        if not self.ceremony_field_order:
            return default_order
        
        # Use custom order if available
        order = self.ceremony_field_order.get('order', [])
        if not order:
            return default_order
        
        # Create ordered list based on saved order
        ordered_fields = []
        field_map = {f['field']: f for f in default_order}
        
        for field_name in order:
            if field_name in field_map:
                ordered_fields.append(field_map[field_name])
        
        # Add any missing fields at the end
        for field_info in default_order:
            if field_info['field'] not in order:
                ordered_fields.append(field_info)
        
        return ordered_fields


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
