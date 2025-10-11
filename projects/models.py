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
        ('ALTELE', 'Altele'),
    ]
    
    STATUS_CHOICES = [
        ('Not Started', 'Not Started'),
        ('Planning', 'Planning'),
        ('Filming', 'Filming'),
        ('Editing', 'Editing'),
        ('Completed', 'Completed'),
    ]
    
    EDIT_STATUS_CHOICES = [
        ('Not Started', 'Not Started'),
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
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Not Started')
    edit_status = models.CharField(max_length=50, choices=EDIT_STATUS_CHOICES, default='Not Started')
    editing_progress = models.IntegerField(default=0, help_text="Editing progress percentage (0-100)")
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
    
    # Main Details (replaces ceremony details for all types)
    main_details = models.TextField(blank=True, null=True, help_text="Main event details")
    
    # Package section fields
    PACKAGE_TYPE_CHOICES = [
        ('Clasic', 'Clasic'),
        ('Highlights', 'Highlights'),
        ('Duo', 'Duo'),
        ('Cinema', 'Cinema'),
        ('Creative', 'Creative'),
        ('Botez', 'Botez'),
        ('Custom', 'Custom'),
    ]
    
    MOVIE_DURATION_CHOICES = [
        ('30min', '30 min'),
        ('1h', '1 h'),
        ('1h30min', '1h30min'),
        ('2h-3h', '2h-3h'),
        ('3h-4h', '3h-4h'),
        ('Other', 'Other'),
    ]
    
    # Package fields
    package_type = models.CharField(max_length=20, choices=PACKAGE_TYPE_CHOICES, blank=True, null=True)
    package_4k = models.BooleanField(default=True)
    package_fullhd = models.BooleanField(default=False)
    package_cameras = models.IntegerField(default=1, choices=[(1, '1'), (2, '2'), (3, '3')])
    
    # Montages
    montage_highlights = models.BooleanField(default=False)
    montage_movie = models.BooleanField(default=False)
    montage_movie_duration = models.CharField(max_length=20, choices=MOVIE_DURATION_CHOICES, blank=True, null=True)
    montage_movie_other = models.CharField(max_length=100, blank=True, null=True)
    montage_bonus_primary = models.BooleanField(default=False)
    montage_bonus_full = models.BooleanField(default=False)
    montage_cinema_duration = models.CharField(max_length=20, choices=[('1h', '1 hour'), ('1h30min', '1h30min')], default='1h30min', blank=True, null=True)
    
    # Equipment details checkboxes
    equipment_audio_recorder = models.BooleanField(default=False)
    equipment_stabilizer = models.BooleanField(default=False)
    equipment_external_light = models.BooleanField(default=False)
    
    # Team numbers
    team_videographer = models.IntegerField(default=1)
    team_operator = models.IntegerField(default=0)
    team_assistant = models.IntegerField(default=0)
    
    # Delivery medium checkboxes
    delivery_online = models.BooleanField(default=True)
    delivery_usb = models.BooleanField(default=False)
    
    # Event presence
    event_presence = models.TextField(blank=True, null=True)
    
    # Price details (admin only)
    CURRENCY_CHOICES = [
        ('EUR', 'Euro'),
        ('LEI', 'Lei'),
    ]
    price = models.IntegerField(blank=True, null=True)
    price_currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='EUR')
    price_other_details = models.TextField(blank=True, null=True)
    
    # Filming details
    filming_details = models.TextField(blank=True, null=True, help_text="Client requests for filming")
    videographer_filming_notes = models.TextField(blank=True, null=True, help_text="Videographer's notes for filming (admin only)")
    critical_production_notes = models.TextField(blank=True, null=True, help_text="Critical production details (admin only)")
    
    # Editing notes
    videographer_editing_notes = models.TextField(blank=True, null=True, help_text="Videographer's notes for editing (admin only)")
    
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
    
    # Client guidance tracking
    current_guidance_message = models.CharField(max_length=50, default='initial', help_text="Current guidance message type")
    dismissed_guidance_messages = models.JSONField(default=list, blank=True, help_text="List of dismissed guidance message types")
    
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
        """Override save to generate slug and update project name based on video title"""
        
        # Auto-update project name based on video title
        if self.title_video and self.title_video.strip():
            # Format: "Type - Video Title" (e.g., "Nunta - Ioana si Ion")
            type_display = dict(self.PROJECT_TYPE_CHOICES).get(self.type, self.type)
            new_name = f"{type_display} - {self.title_video.strip()}"
            if self.name != new_name:
                self.name = new_name
        
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
        """Return main details field for all project types"""
        # For ALTELE type, only show Main Details
        if self.type == 'ALTELE':
            return [
                {'field': 'main_details', 'label': 'Main Details', 'rows': 8}
            ]
        
        # For NUNTA and BOTEZ, show traditional ceremony fields
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
    
    def get_package_fields(self):
        """Return Package section fields for client view"""
        return {
            'package_type': {'label': 'Package Type', 'type': 'select', 'choices': self.PACKAGE_TYPE_CHOICES},
            'package_4k': {'label': '4K', 'type': 'checkbox'},
            'package_cameras': {'label': 'No of cameras', 'type': 'radio', 'choices': [(1, '1'), (2, '2'), (3, '3')]},
            'montage_highlights': {'label': 'Highlights clip', 'type': 'checkbox'},
            'montage_movie': {'label': 'Movie', 'type': 'checkbox'},
            'montage_movie_duration': {'label': 'Movie Duration', 'type': 'select', 'choices': self.MOVIE_DURATION_CHOICES},
            'montage_movie_other': {'label': 'Other Duration', 'type': 'text'},
            'montage_bonus_primary': {'label': 'Primary edit (aprox 4 h)', 'type': 'checkbox'},
            'montage_bonus_full': {'label': 'Full Movie', 'type': 'checkbox'},
            'equipment_audio_recorder': {'label': 'External audio recorder(s)', 'type': 'checkbox'},
            'equipment_stabilizer': {'label': 'Stabilizer', 'type': 'checkbox'},
            'equipment_external_light': {'label': 'External light', 'type': 'checkbox'},
            'team_videographer': {'label': 'Videographer', 'type': 'number'},
            'team_operator': {'label': 'Operator', 'type': 'number'},
            'team_assistant': {'label': 'Assistant', 'type': 'number'},
            'delivery_online': {'label': 'Online', 'type': 'checkbox'},
            'delivery_usb': {'label': 'USB memory stick', 'type': 'checkbox'},
            'event_presence': {'label': 'Event presence', 'type': 'textarea'},
        }
    
    def get_client_guidance_message(self):
        """Get the appropriate guidance message based on project status"""
        messages = {
            'initial': "Please review all the details carefully and add or improve your preferences in the specific areas. Your input helps us create the perfect video for your special day.",
            'planning': "The project is now in planning phase. Please ensure all your preferences are clearly stated in each section.",
            'filming': "Filming is scheduled. Review the production details and add any last-minute requests or special moments you want captured.",
            'editing': "Your video is being edited. Check the editing preferences and package details to ensure they match your vision.",
            'review': "Your video is ready for review. Please provide detailed feedback in the appropriate sections.",
            'completed': "Your project is complete! Thank you for choosing us. Feel free to leave any final feedback.",
        }
        
        # Determine message type based on status
        if self.status == 'Planning':
            message_type = 'planning'
        elif self.status == 'Filming':
            message_type = 'filming'
        elif self.edit_status in ['In Progress', 'Review']:
            message_type = 'editing' if self.edit_status == 'In Progress' else 'review'
        elif self.status == 'Completed' or self.edit_status == 'Completed':
            message_type = 'completed'
        else:
            message_type = 'initial'
        
        # Update current message type if it changed
        if self.current_guidance_message != message_type:
            self.current_guidance_message = message_type
            # Reset dismissed messages when status changes
            self.dismissed_guidance_messages = []
            self.save(update_fields=['current_guidance_message', 'dismissed_guidance_messages'])
        
        return messages.get(message_type, messages['initial']), message_type
    
    def should_show_guidance(self):
        """Check if the current guidance message should be shown"""
        message_text, message_type = self.get_client_guidance_message()
        return message_type not in self.dismissed_guidance_messages


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
        return f"{size:.1f} PB"


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


class FieldHistory(models.Model):
    """Track history of field changes with editor information"""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='field_history')
    field_name = models.CharField(max_length=100, help_text="Name of the field that was changed")
    old_value = models.TextField(blank=True, null=True, help_text="Previous instructions")
    new_value = models.TextField(blank=True, null=True, help_text="New instructions")
    edited_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='field_edits')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Field History"
        verbose_name_plural = "Field Histories"
    
    def __str__(self):
        editor_name = self.edited_by.get_full_name() if self.edited_by and self.edited_by.get_full_name() else (self.edited_by.email if self.edited_by else 'Unknown')
        return f"{self.project.name} - {self.field_name} by {editor_name}"
