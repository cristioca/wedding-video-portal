from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils import timezone
from django.utils.text import slugify
import re


class CustomUserManager(BaseUserManager):
    """Custom user manager for email-based authentication"""
    
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'ADMIN')
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Custom User model with role field and optional username"""
    ROLE_CHOICES = [
        ('ADMIN', 'Admin'),
        ('CLIENT', 'Client'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='CLIENT')
    
    # Make username optional and use email as primary identifier
    username = models.CharField(max_length=150, blank=True, null=True, unique=False)
    email = models.EmailField(unique=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name']  # Remove username from required fields
    
    objects = CustomUserManager()
    
    def is_admin(self):
        return self.role == 'ADMIN'
    
    def is_client(self):
        return self.role == 'CLIENT'
    
    def save(self, *args, **kwargs):
        """Auto-generate username from email if not provided"""
        if not self.username:
            # Generate username from email (before @ symbol)
            email_prefix = self.email.split('@')[0] if self.email else 'user'
            base_username = email_prefix
            counter = 1
            
            # Ensure uniqueness
            while User.objects.filter(username=base_username).exclude(pk=self.pk).exists():
                base_username = f"{email_prefix}{counter}"
                counter += 1
            
            self.username = base_username
        
        super().save(*args, **kwargs)


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
    last_admin_notification_date = models.DateTimeField(blank=True, null=True)
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
    
    def should_notify_admin(self):
        """Check if admin should be notified (respecting 1-hour cooldown)"""
        if not self.last_admin_notification_date:
            return True
        
        from django.utils import timezone
        time_since_last = timezone.now() - self.last_admin_notification_date
        return time_since_last.total_seconds() >= 3600  # 1 hour cooldown
    
    def notify_admin_of_changes(self, modified_by_user):
        """Send email notification to admin about client changes"""
        if not self.should_notify_admin():
            return False
            
        from django.core.mail import send_mail
        from django.conf import settings
        from django.utils import timezone
        
        # Get all admin users
        admin_users = User.objects.filter(role='ADMIN')
        if not admin_users.exists():
            return False
        
        admin_emails = [admin.email for admin in admin_users if admin.email]
        if not admin_emails:
            return False
        
        try:
            send_mail(
                subject=f'Client Modified Project: {self.name}',
                message=f'''
                A client has made changes to project "{self.name}".
                
                Modified by: {modified_by_user.get_full_name() or modified_by_user.email}
                Project: {self.name}
                Event Date: {self.event_date.strftime('%B %d, %Y')}
                
                Please review the changes in the admin panel.
                
                Best regards,
                Wedding Video Portal
                ''',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=admin_emails,
                fail_silently=False,
            )
            
            self.last_admin_notification_date = timezone.now()
            self.admin_notified_of_changes = True
            self.save(update_fields=['last_admin_notification_date', 'admin_notified_of_changes'])
            return True
            
        except Exception as e:
            print(f"Failed to send admin notification: {e}")
            return False
    
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
            {'field': 'prep', 'label': 'Preparation', 'rows': 2},
            {'field': 'church', 'label': 'Church', 'rows': 2},
            {'field': 'session', 'label': 'Photo Session', 'rows': 2},
            {'field': 'restaurant', 'label': 'Restaurant', 'rows': 2}
        ]
        
        # Add Civil Union Details only for wedding projects (NUNTA)
        if self.type == 'NUNTA':
            default_order.insert(0, {'field': 'civil_union_details', 'label': 'Civil Union Details', 'rows': 3})
        
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
