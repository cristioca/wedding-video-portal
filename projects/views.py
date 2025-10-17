from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail, EmailMessage
from django.conf import settings
from django.http import HttpResponse, JsonResponse, FileResponse
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from datetime import datetime
from django.db.models import Q
from .models import Project, File, FileDownloadEvent, ProjectModification, User, FieldHistory
from .forms import LoginForm, ProjectForm, ProjectDetailForm, FileUploadForm
import json
import secrets
import string


def send_rejection_email(modification, rejection_reason, admin_user):
    """Send rejection email to client with CC to admin"""
    project = modification.project
    client_email = project.client_email
    
    if not client_email:
        raise Exception("No client email found for this project")
    
    # Get admin emails for CC
    admin_users = User.objects.filter(role='ADMIN')
    admin_emails = [admin.email for admin in admin_users if admin.email]
    
    # Prepare email content
    field_display_name = modification.field_name.replace('_', ' ').title()
    
    subject = f'Change Request Rejected - {project.name}'
    
    message = f'''Dear {project.client_name or 'Client'},

Your change request for the project "{project.name}" has been reviewed and rejected.

Project Details:
- Project: {project.name}
- Event Date: {project.event_date.strftime('%B %d, %Y')}
- Field: {field_display_name}
- Your Requested Change: {modification.new_value}

Rejection Reason:
{rejection_reason}

What's Next:
Please review the feedback above and feel free to submit a new change request with the necessary corrections. If you have any questions, please don't hesitate to contact us.

Best regards,
{admin_user.get_full_name() or admin_user.email}
Wedding Video Portal Team

---
This is an automated message from the Wedding Video Portal system.
'''
    
    try:
        # Send email to client with CC to admins using EmailMessage
        email = EmailMessage(
            subject=subject,
            body=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[client_email],
            cc=admin_emails,
        )
        email.send(fail_silently=False)
        return True
    except Exception as e:
        raise Exception(f"Failed to send rejection email: {str(e)}")


def home(request):
    """Home page - redirects to login or dashboard"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    return redirect('login')


def login_view(request):
    """Login view"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['username']  # Field is named 'username' but contains email
            password = form.cleaned_data['password']
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.get_full_name() or user.email}!')
                return redirect('dashboard')
            else:
                messages.error(request, 'Invalid email or password.')
    else:
        form = LoginForm()
    
    return render(request, 'login.html', {'form': form})


def logout_view(request):
    """Logout view"""
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('login')


@login_required
def dashboard(request):
    """Dashboard view - shows projects based on user role"""
    user = request.user
    search_query = request.GET.get('search', '')
    sort_by = request.GET.get('sort', 'date')  # Default sort by event date (earliest first)
    include_archived = request.GET.get('include_archived', '') == 'on'
    
    # Valid sort options
    valid_sorts = {
        'name': 'name',
        '-name': '-name',
        'date': 'event_date',
        '-date': '-event_date',
        'status': 'status',
        '-status': '-status',
        'client': 'client_name',
        '-client': '-client_name',
        'newest': '-id',
        'oldest': 'id'
    }
    
    # Use valid sort or default
    sort_field = valid_sorts.get(sort_by, '-id')
    
    if user.is_admin():
        # Admin sees all projects
        if include_archived:
            projects = Project.objects.all()  # Include both archived and active
        else:
            projects = Project.objects.filter(is_archived=False)
        pending_modifications = ProjectModification.objects.filter(status='PENDING')
        
        # Apply search filter
        if search_query:
            projects = projects.filter(
                Q(name__icontains=search_query) |
                Q(client_name__icontains=search_query) |
                Q(user__username__icontains=search_query) |
                Q(user__first_name__icontains=search_query) |
                Q(user__last_name__icontains=search_query) |
                Q(status__icontains=search_query) |
                Q(type__icontains=search_query)
            )
        
        projects = projects.order_by(sort_field)
        
        context = {
            'projects': projects,
            'pending_modifications': pending_modifications,
            'is_admin': True,
            'search_query': search_query,
            'current_sort': sort_by,
            'include_archived': include_archived,
        }
    else:
        # Client sees only their projects
        if include_archived:
            projects = Project.objects.filter(user=user)  # Include both archived and active
        else:
            projects = Project.objects.filter(user=user, is_archived=False)
        
        # Apply search filter
        if search_query:
            projects = projects.filter(
                Q(name__icontains=search_query) |
                Q(client_name__icontains=search_query) |
                Q(status__icontains=search_query) |
                Q(type__icontains=search_query)
            )
        
        projects = projects.order_by(sort_field)
        
        context = {
            'projects': projects,
            'is_admin': False,
            'search_query': search_query,
            'current_sort': sort_by,
            'include_archived': include_archived,
        }
    
    return render(request, 'dashboard.html', context)


@login_required
def project_detail(request, slug):
    """Project detail view"""
    project = get_object_or_404(Project, slug=slug)
    
    # Check permissions
    if not request.user.is_admin() and project.user != request.user:
        messages.error(request, 'You do not have permission to view this project.')
        return redirect('dashboard')
    if request.method == 'POST':
        if 'update_project' in request.POST:
            if request.user.is_client():
                # Fields that bypass approval workflow (apply immediately for clients)
                bypass_approval_fields = ['filming_details', 'notes']
                
                # For clients: Don't bind form to instance to prevent automatic changes
                form = ProjectDetailForm(request.POST)
                if form.is_valid():
                    # Get original values from database
                    original_project = Project.objects.get(pk=project.pk)
                    
                    has_pending_changes = False
                    has_direct_changes = False
                    
                    # Track modifications and apply bypass field changes
                    for field_name, new_value in form.cleaned_data.items():
                        old_value = str(getattr(original_project, field_name) or '')
                        new_value_str = str(new_value or '')
                        
                        # Only process if value actually changed
                        if old_value != new_value_str:
                            if field_name in bypass_approval_fields:
                                # Apply changes immediately for bypass fields
                                setattr(project, field_name, new_value)
                                has_direct_changes = True
                                
                                # Create AUTO_APPLIED modification record
                                ProjectModification.objects.create(
                                    project=project,
                                    field_name=field_name,
                                    old_value=old_value,
                                    new_value=new_value_str,
                                    created_by=request.user,
                                    status='AUTO_APPLIED'
                                )
                                
                                # Create field history
                                FieldHistory.objects.create(
                                    project=project,
                                    field_name=field_name,
                                    old_value=old_value,
                                    new_value=new_value_str,
                                    edited_by=request.user
                                )
                            else:
                                # Create PENDING modification for other fields
                                ProjectModification.objects.create(
                                    project=project,
                                    field_name=field_name,
                                    old_value=old_value,
                                    new_value=new_value_str,
                                    created_by=request.user,
                                    status='PENDING'
                                )
                                has_pending_changes = True
                    
                    if has_pending_changes:
                        project.admin_notified_of_changes = True
                        project.has_unsent_changes = True
                    
                    project.save()
                    
                    # Send email notification to admin only if there are pending changes
                    if has_pending_changes:
                        if project.notify_admin_of_changes(request.user):
                            messages.info(request, 'Your changes have been submitted for admin approval and administrators have been notified.')
                        else:
                            messages.info(request, 'Your changes have been submitted for admin approval.')
                    elif has_direct_changes:
                        messages.success(request, 'Your changes have been saved successfully.')
                    
            else:
                # For admins: Apply changes immediately
                form = ProjectDetailForm(request.POST, instance=project)
                if form.is_valid():
                    form.save()
                    messages.success(request, 'Project updated successfully.')
            
            return redirect('project_detail', slug=project.slug)
        
        elif 'upload_file' in request.POST:
            file_form = FileUploadForm(request.POST, request.FILES)
            if file_form.is_valid():
                file = file_form.save(commit=False)
                file.project = project
                file.uploaded_by = request.user
                file.size_bytes = request.FILES['file'].size
                file.save()
                messages.success(request, 'File uploaded successfully.')
                return redirect('project_detail', pk=project.pk)
    else:
        form = ProjectDetailForm(instance=project)
        file_form = FileUploadForm()
    
    files = project.files.all()
    modifications = project.modifications.filter(status='PENDING') if request.user.is_admin() else None
    ceremony_fields = project.get_ceremony_fields_ordered()
    
    # Get field history for filming_details and notes
    filming_details_history = project.field_history.filter(field_name='filming_details').order_by('-created_at')
    notes_history = project.field_history.filter(field_name='notes').order_by('-created_at')
    
    # Package presets for client-side use
    package_presets = {
        'Clasic': {
            'package_type': 'Clasic',
            'package_4k': True, 'package_fullhd': False, 'package_cameras': 1,
            'montage_highlights': True, 'montage_movie': True, 'montage_bonus_primary': False, 'montage_bonus_full': False,
            'montage_movie_duration': '2h-3h', 'montage_cinema_duration': '1h30min',
            'equipment_audio_recorder': True, 'equipment_stabilizer': True, 'equipment_external_light': False,
            'team_videographer': 1, 'team_operator': 0, 'team_assistant': 0,
            'delivery_online': True, 'delivery_usb': False
        },
        'Highlights': {
            'package_type': 'Highlights',
            'package_4k': True, 'package_fullhd': False, 'package_cameras': 2,
            'montage_highlights': True, 'montage_movie': False, 'montage_bonus_primary': False, 'montage_bonus_full': True,
            'montage_movie_duration': '', 'montage_cinema_duration': '1h',
            'equipment_audio_recorder': True, 'equipment_stabilizer': True, 'equipment_external_light': True,
            'team_videographer': 1, 'team_operator': 0, 'team_assistant': 1,
            'delivery_online': True, 'delivery_usb': False
        },
        'Duo': {
            'package_type': 'Duo',
            'package_4k': True, 'package_fullhd': False, 'package_cameras': 2,
            'montage_highlights': True, 'montage_movie': True, 'montage_bonus_primary': False, 'montage_bonus_full': False,
            'montage_movie_duration': '3h-4h', 'montage_cinema_duration': '1h30min',
            'equipment_audio_recorder': True, 'equipment_stabilizer': True, 'equipment_external_light': False,
            'team_videographer': 1, 'team_operator': 1, 'team_assistant': 0,
            'delivery_online': True, 'delivery_usb': False
        },
        'Cinema': {
            'package_type': 'Cinema',
            'package_4k': True, 'package_fullhd': False, 'package_cameras': 2,
            'montage_highlights': True, 'montage_movie': False, 'montage_bonus_primary': True, 'montage_bonus_full': True,
            'montage_movie_duration': '', 'montage_cinema_duration': '1h30min',
            'equipment_audio_recorder': True, 'equipment_stabilizer': True, 'equipment_external_light': True,
            'team_videographer': 2, 'team_operator': 0, 'team_assistant': 0,
            'delivery_online': True, 'delivery_usb': False
        },
        'Creative': {
            'package_type': 'Creative',
            'package_4k': True, 'package_fullhd': False, 'package_cameras': 3,
            'montage_highlights': True, 'montage_movie': True, 'montage_bonus_primary': False, 'montage_bonus_full': True,
            'montage_movie_duration': '3h-4h', 'montage_cinema_duration': '1h30min',
            'equipment_audio_recorder': True, 'equipment_stabilizer': True, 'equipment_external_light': True,
            'team_videographer': 2, 'team_operator': 1, 'team_assistant': 0,
            'delivery_online': True, 'delivery_usb': True
        },
        'Botez': {
            'package_type': 'Botez',
            'package_4k': True, 'package_fullhd': False, 'package_cameras': 1,
            'montage_highlights': True, 'montage_movie': True, 'montage_bonus_primary': False, 'montage_bonus_full': False,
            'montage_movie_duration': '2h-3h', 'montage_cinema_duration': '1h30min',
            'equipment_audio_recorder': True, 'equipment_stabilizer': True, 'equipment_external_light': False,
            'team_videographer': 1, 'team_operator': 0, 'team_assistant': 0,
            'delivery_online': True, 'delivery_usb': False
        },
        'Custom': {
            'package_type': 'Custom',
            'package_4k': True, 'package_fullhd': False, 'package_cameras': 1,
            'montage_highlights': False, 'montage_movie': False, 'montage_bonus_primary': False, 'montage_bonus_full': False,
            'montage_movie_duration': '', 'montage_cinema_duration': '1h30min',
            'equipment_audio_recorder': False, 'equipment_stabilizer': False, 'equipment_external_light': False,
            'team_videographer': 1, 'team_operator': 0, 'team_assistant': 0,
            'delivery_online': True, 'delivery_usb': False
        }
    }
    
    # Get guidance message info for clients
    guidance_message = None
    guidance_message_type = None
    show_guidance = False
    
    if request.user.is_client() and project.user == request.user:
        guidance_message, guidance_message_type = project.get_client_guidance_message()
        show_guidance = project.should_show_guidance()
    
    context = {
        'project': project,
        'form': form,
        'file_form': file_form,
        'files': files,
        'modifications': modifications,
        'is_admin': request.user.is_admin(),
        'ceremony_fields': ceremony_fields,
        'package_presets': json.dumps(package_presets),
        'filming_details_history': filming_details_history,
        'notes_history': notes_history,
        'guidance_message': guidance_message,
        'guidance_message_type': guidance_message_type,
        'show_guidance': show_guidance,
    }
    
    return render(request, 'project_detail.html', context)


@login_required
def create_project(request):
    """Create new project - admin only"""
    if not request.user.is_admin():
        messages.error(request, 'Only administrators can create projects.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            # Set defaults for required fields not in form
            project.status = 'Not Started'
            project.edit_status = 'Not Started'
            
            # Handle client user creation/assignment
            client_email = form.cleaned_data.get('client_email')
            client_name = form.cleaned_data.get('client_name')
            
            if client_email:
                try:
                    # Reuse existing user account for the same email
                    client_user = User.objects.get(email=client_email)
                    # Update name if provided and different
                    if client_name:
                        name_parts = client_name.split()
                        if name_parts and client_user.first_name != name_parts[0]:
                            client_user.first_name = name_parts[0] if len(name_parts) > 0 else ''
                            client_user.last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''
                            client_user.save()
                            
                            # Update client_name in ALL projects for this user
                            User.objects.filter(email=client_email).update(
                                first_name=client_user.first_name,
                                last_name=client_user.last_name
                            )
                            Project.objects.filter(user=client_user).update(client_name=client_name)
                            
                except User.DoesNotExist:
                    # Create new client user
                    name_parts = client_name.split() if client_name else ['', '']
                    client_user = User.objects.create_user(
                        email=client_email,
                        first_name=name_parts[0] if len(name_parts) > 0 else '',
                        last_name=' '.join(name_parts[1:]) if len(name_parts) > 1 else '',
                        role='CLIENT',
                        password='temp_password_needs_reset'
                    )
                
                project.user = client_user
                # Store client data in project for consistency
                project.client_email = client_email
                project.client_name = client_name
            else:
                # Email is required for projects now
                messages.error(request, 'Client email is required for creating projects.')
                return render(request, 'project_form.html', {'form': form, 'title': 'Create Project'})
            project.save()
            messages.success(request, f'Project "{project.name}" created successfully.')
            return redirect('project_detail', slug=project.slug)
    else:
        form = ProjectForm()
    
    return render(request, 'project_form.html', {'form': form, 'title': 'Create Project'})


@login_required
def archive_project(request, slug):
    """Archive a project - admin only"""
    if not request.user.is_admin():
        messages.error(request, 'Only administrators can archive projects.')
        return redirect('dashboard')
    
    project = get_object_or_404(Project, slug=slug)
    project.is_archived = True
    project.save()
    
    messages.success(request, f'Project "{project.name}" has been archived.')
    return redirect('dashboard')


@login_required
def delete_project(request, slug):
    """Delete project permanently - admin only"""
    if not request.user.is_admin():
        messages.error(request, 'Only administrators can delete projects.')
        return redirect('dashboard')
    
    project = get_object_or_404(Project, slug=slug)
    project_name = project.name
    project.delete()
    
    messages.success(request, f'Project "{project_name}" has been deleted permanently.')
    return redirect('dashboard')


@login_required
def archived_projects(request):
    """View archived projects - admin only"""
    if not request.user.is_admin():
        messages.error(request, 'Only administrators can view archived projects.')
        return redirect('dashboard')
    
    projects = Project.objects.filter(is_archived=True).order_by('-id')
    
    context = {
        'projects': projects,
        'is_admin': True,
        'page_title': 'Archived Projects'
    }
    
    return render(request, 'archived_projects.html', context)


@login_required
def download_file(request, file_id):
    """Download a file"""
    file = get_object_or_404(File, pk=file_id)
    project = file.project
    
    # Check permissions
    if not request.user.is_admin() and project.user != request.user:
        messages.error(request, 'You do not have permission to download this file.')
        return redirect('dashboard')
    
    # Track download
    FileDownloadEvent.objects.create(
        file=file,
        project=project,
        downloaded_by=request.user,
        success=True
    )
    
    # Serve file
    response = FileResponse(file.file, as_attachment=True, filename=file.display_name)
    return response


@login_required
def notify_client(request, slug):
    """Send notification email to client - admin only"""
    if not request.user.is_admin():
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    project = get_object_or_404(Project, slug=slug)
    
    # Parse request body to check for force parameter
    force_send = False
    if request.content_type == 'application/json':
        try:
            import json
            body = json.loads(request.body)
            force_send = body.get('force', False)
        except:
            pass
    
    # Check if we should send notification (unless forced)
    if not force_send and project.last_client_notification_date:
        time_since_last = timezone.now() - project.last_client_notification_date
        if time_since_last.total_seconds() < 3600:  # 1 hour cooldown
            minutes_remaining = int((3600 - time_since_last.total_seconds()) / 60) + 1
            return JsonResponse({
                'cooldown': True, 
                'minutes_remaining': minutes_remaining,
                'message': f'A notification was sent {int(time_since_last.total_seconds() / 60)} minutes ago. Send another one anyway?'
            })
    
    # Send email
    try:
        send_mail(
            subject=f'Update on your project: {project.name}',
            message=f'''
            Dear {project.user.get_full_name() or project.user.username},
            
            There has been an update to your wedding video project "{project.name}".
            
            Current Status: {project.status}
            Edit Status: {project.edit_status}
            
            Please log in to the portal to view the details:
            {request.build_absolute_uri('/dashboard/')}
            
            Best regards,
            Wedding Video Portal Team
            ''',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[project.user.email],
            fail_silently=False,
        )
        
        project.last_client_notification_date = timezone.now()
        project.has_unsent_changes = False
        project.save()
        
        return JsonResponse({'success': True, 'message': 'Notification sent successfully'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def update_project_field(request, slug):
    """Update a single project field via AJAX"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    project = get_object_or_404(Project, slug=slug)
    
    # Check permissions
    if not request.user.is_admin() and project.user != request.user:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    try:
        data = json.loads(request.body)
        field_name = data.get('field_name')
        field_value = data.get('field_value')
        
        if not field_name:
            return JsonResponse({'error': 'Field name is required'}, status=400)
        
        # Validate field exists on model
        if not hasattr(project, field_name):
            return JsonResponse({'error': 'Invalid field name'}, status=400)
        
        # Store old value for modification tracking
        old_value = str(getattr(project, field_name) or '')
        
        # Handle different field types
        field = project._meta.get_field(field_name)
        
        # Handle boolean fields
        if field.__class__.__name__ == 'BooleanField':
            if isinstance(field_value, str):
                field_value = field_value.lower() in ('true', '1', 'yes', 'on')
            elif not isinstance(field_value, bool):
                field_value = bool(field_value)
        
        # Handle integer fields
        elif field.__class__.__name__ == 'IntegerField':
            try:
                field_value = int(field_value) if field_value != '' else 0
            except (ValueError, TypeError):
                return JsonResponse({'error': f'Invalid integer value for {field_name}'}, status=400)
        
        # Handle choice fields
        elif hasattr(field, 'choices') and field.choices:
            # Validate choice field
            valid_choices = [choice[0] for choice in field.choices]
            if field_value not in valid_choices and field_value != '':
                return JsonResponse({'error': 'Invalid choice'}, status=400)
        
        # Fields that bypass approval workflow (apply immediately for both admin and client)
        bypass_approval_fields = ['filming_details', 'notes']
        
        # Track modifications if client is editing (except bypass fields)
        if request.user.is_client() and field_name not in bypass_approval_fields:
            ProjectModification.objects.create(
                project=project,
                field_name=field_name,
                old_value=old_value,
                new_value=str(field_value),
                created_by=request.user,
                status='PENDING'
            )
            project.admin_notified_of_changes = True
            project.has_unsent_changes = True
            project.save()
            
            # Send email notification to admin
            project.notify_admin_of_changes(request.user)
            return JsonResponse({
                'success': True, 
                'message': 'Change submitted for admin approval',
                'pending_approval': True
            })
        
        # Admin changes OR client changes to bypass fields are applied immediately
        if request.user.is_admin() or field_name in bypass_approval_fields:
            # Convert date strings for DateTimeField where needed
            if field_name == 'event_date':
                # Accept either 'YYYY-MM-DD' or 'YYYY-MM-DDTHH:MM'
                parsed = None
                try:
                    if isinstance(field_value, str):
                        if 'T' in field_value:
                            # datetime-local format
                            parsed = datetime.strptime(field_value, '%Y-%m-%dT%H:%M')
                        else:
                            # date-only, default to midnight
                            parsed = datetime.strptime(field_value, '%Y-%m-%d')
                    if parsed is not None:
                        # Make timezone-aware using current timezone
                        tz = timezone.get_current_timezone()
                        field_value = timezone.make_aware(parsed, tz)
                except Exception:
                    return JsonResponse({'error': 'Invalid date format for event_date'}, status=400)

            setattr(project, field_name, field_value)
            
            # Admin-only fields that should NOT trigger client notification
            admin_only_fields = [
                'videographer_filming_notes',
                'critical_production_notes', 
                'videographer_editing_notes',
                'price',
                'price_currency',
                'price_other_details'
            ]
            
            # Mark that there are changes not yet notified to the client
            # BUT only if the field is visible to clients
            if field_name not in admin_only_fields:
                project.has_unsent_changes = True
            
            project.save()  # The save method will auto-update project name if title_video changed
            
            # Create auto-applied modification record
            ProjectModification.objects.create(
                project=project,
                field_name=field_name,
                old_value=old_value,
                new_value=str(field_value),
                created_by=request.user,
                status='AUTO_APPLIED'
            )
            
            # Track field history for specific fields (filming_details, notes)
            if field_name in ['filming_details', 'notes']:
                print(f"🔍 Field History Check: field={field_name}, old='{old_value}', new='{str(field_value)}'")
                if old_value != str(field_value):
                    history_entry = FieldHistory.objects.create(
                        project=project,
                        field_name=field_name,
                        old_value=old_value,
                        new_value=str(field_value),
                        edited_by=request.user
                    )
                    print(f"✅ Field History Created: ID={history_entry.id}, by={request.user.email}")
                else:
                    print(f"⏭️ No change detected, skipping history entry")
            
            return JsonResponse({
                'success': True, 
                'message': 'Field updated successfully',
                'new_value': str(getattr(project, field_name))
            })
            
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def batch_update_project(request, slug):
    """Update multiple project fields in a single request (for package presets)"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    project = get_object_or_404(Project, slug=slug)
    
    # Check permissions
    if not request.user.is_admin() and project.user != request.user:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    try:
        updates = json.loads(request.body)
        print(f"📦 BATCH UPDATE REQUEST for {slug}: {updates}")
        
        if not isinstance(updates, dict):
            return JsonResponse({'error': 'Updates must be a dictionary'}, status=400)
        
        updated_fields = []
        original_values = {}  # Store original values before any changes
        processed_updates = {}  # Store processed field values
        
        # First pass: capture original values and validate fields
        for field_name, field_value in updates.items():
            # Validate field exists on model
            if not hasattr(project, field_name):
                continue  # Skip invalid fields
            
            try:
                field = project._meta.get_field(field_name)
                
                # Store original value before any changes
                original_values[field_name] = str(getattr(project, field_name) or '')
                
                # Handle boolean fields
                if field.__class__.__name__ == 'BooleanField':
                    if isinstance(field_value, str):
                        field_value = field_value.lower() in ('true', '1', 'yes', 'on')
                    elif not isinstance(field_value, bool):
                        field_value = bool(field_value)
                
                # Handle integer fields
                elif field.__class__.__name__ == 'IntegerField':
                    try:
                        field_value = int(field_value) if field_value != '' else 0
                    except (ValueError, TypeError):
                        continue  # Skip invalid values
                
                # Handle choice fields
                elif hasattr(field, 'choices') and field.choices:
                    valid_choices = [choice[0] for choice in field.choices]
                    if field_value not in valid_choices and field_value != '':
                        continue  # Skip invalid choices
                
                # Store processed value
                processed_updates[field_name] = field_value
                updated_fields.append(field_name)
                
            except Exception:
                continue  # Skip fields that cause errors
        
        # Fields that bypass approval workflow
        bypass_approval_fields = ['filming_details', 'notes']
        
        # Apply changes for admins or bypass fields for clients
        if request.user.is_admin():
            # Apply changes immediately for admins
            for field_name, field_value in processed_updates.items():
                setattr(project, field_name, field_value)
            
            print(f"💾 SAVING {len(updated_fields)} fields: {updated_fields}")
            
            # Admin-only fields that should NOT trigger client notification
            admin_only_fields = [
                'videographer_filming_notes',
                'critical_production_notes', 
                'videographer_editing_notes',
                'price',
                'price_currency',
                'price_other_details'
            ]
            
            # Check if any client-visible fields were updated
            client_visible_fields = [f for f in updated_fields if f not in admin_only_fields]
            if client_visible_fields:
                project.has_unsent_changes = True
            
            try:
                project.save()
                print(f"✅ PROJECT SAVED SUCCESSFULLY")
            except Exception as save_error:
                print(f"❌ DATABASE SAVE ERROR: {save_error}")
                return JsonResponse({'error': f'Database error: {str(save_error)}'}, status=500)
        else:
            # For clients: Apply changes only for bypass fields
            bypass_fields_to_save = [f for f in updated_fields if f in bypass_approval_fields]
            pending_fields = [f for f in updated_fields if f not in bypass_approval_fields]
            
            if bypass_fields_to_save:
                for field_name in bypass_fields_to_save:
                    setattr(project, field_name, processed_updates[field_name])
                project.save()
                print(f"✅ CLIENT: Applied {len(bypass_fields_to_save)} bypass fields: {bypass_fields_to_save}")
            
            if pending_fields:
                print(f"📝 CLIENT BATCH UPDATE: {len(pending_fields)} fields queued for approval: {pending_fields}")
        
        # Track modifications
        if updated_fields:
            try:
                for field_name in updated_fields:
                    # Determine status and value based on user and field type
                    if request.user.is_client():
                        new_value = str(processed_updates.get(field_name, '') or '')
                        # Bypass fields get AUTO_APPLIED status for clients too
                        status = 'AUTO_APPLIED' if field_name in bypass_approval_fields else 'PENDING'
                    else:
                        new_value = str(getattr(project, field_name) or '')
                        status = 'AUTO_APPLIED'
                    
                    ProjectModification.objects.create(
                        project=project,
                        field_name=field_name,
                        old_value=original_values.get(field_name, ''),
                        new_value=new_value,
                        created_by=request.user,
                        status=status
                    )
                    
                    # Track field history for specific fields (filming_details, notes) for both admin and client
                    if field_name in ['filming_details', 'notes']:
                        old_val = original_values.get(field_name, '')
                        if old_val != new_value:
                            history_entry = FieldHistory.objects.create(
                                project=project,
                                field_name=field_name,
                                old_value=old_val,
                                new_value=new_value,
                                edited_by=request.user
                            )
                            print(f"📜 Field History Created: {field_name} by {request.user.email} (ID={history_entry.id})")
                
                print(f"📝 CREATED {len(updated_fields)} MODIFICATION RECORDS")
            except Exception as mod_error:
                print(f"⚠️ MODIFICATION TRACKING ERROR: {mod_error}")
                # Don't fail the whole request for tracking errors
        
        # Handle notifications and project state
        if request.user.is_client() and updated_fields:
            # Check if there are any pending fields (not bypass fields)
            pending_fields = [f for f in updated_fields if f not in bypass_approval_fields]
            
            if pending_fields:
                # Mark project as having unsent changes only if there are pending fields
                project.admin_notified_of_changes = True
                project.has_unsent_changes = True
                project.save()
                
                # Notify admin if client made pending changes
                if project.should_notify_admin():
                    try:
                        project.notify_admin_of_changes(request.user)
                        print(f"📧 ADMIN NOTIFICATION SENT for {len(pending_fields)} pending fields")
                    except Exception as notify_error:
                        print(f"⚠️ NOTIFICATION ERROR: {notify_error}")
                        # Don't fail the whole request for notification errors
        
        print(f"🎉 BATCH UPDATE COMPLETED SUCCESSFULLY")
        
        if request.user.is_client():
            bypass_fields_updated = [f for f in updated_fields if f in bypass_approval_fields]
            pending_fields_updated = [f for f in updated_fields if f not in bypass_approval_fields]
            
            if bypass_fields_updated and pending_fields_updated:
                message = f'{len(bypass_fields_updated)} changes saved, {len(pending_fields_updated)} changes submitted for approval'
                return JsonResponse({
                    'success': True, 
                    'message': message,
                    'pending_approval': True,
                    'updated_fields': updated_fields
                }, status=202)
            elif bypass_fields_updated:
                message = f'{len(bypass_fields_updated)} changes saved successfully'
                return JsonResponse({
                    'success': True, 
                    'message': message,
                    'pending_approval': False,
                    'updated_fields': updated_fields
                })
            else:
                message = f'{len(pending_fields_updated)} changes submitted for admin approval'
                return JsonResponse({
                    'success': True, 
                    'message': message,
                    'pending_approval': True,
                    'updated_fields': updated_fields
                }, status=202)
        else:
            return JsonResponse({
                'success': True, 
                'message': f'Updated {len(updated_fields)} fields successfully',
                'updated_fields': updated_fields
            }, status=200)
        
    except json.JSONDecodeError as json_error:
        print(f"❌ JSON DECODE ERROR: {json_error}")
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        print(f"❌ BATCH UPDATE ERROR: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def approve_modification(request, mod_id):
    """Approve or reject a modification - admin only"""
    if not request.user.is_admin():
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    modification = get_object_or_404(ProjectModification, pk=mod_id)
    action = request.POST.get('action')
    
    if action == 'approve':
        # Apply the change
        project = modification.project
        new_val = modification.new_value
        # Convert date strings when applying approved changes
        if modification.field_name == 'event_date':
            try:
                if isinstance(new_val, str):
                    if 'T' in new_val:
                        dt = datetime.strptime(new_val, '%Y-%m-%dT%H:%M')
                    else:
                        dt = datetime.strptime(new_val, '%Y-%m-%d')
                else:
                    dt = new_val
                tz = timezone.get_current_timezone()
                new_val = timezone.make_aware(dt, tz) if isinstance(dt, datetime) and dt.tzinfo is None else dt
            except Exception:
                messages.error(request, 'Invalid date format in approved modification for event_date.')
                return redirect('project_detail', pk=project.pk)

        setattr(project, modification.field_name, new_val)
        # Mark as having unnotified changes (client should be notified)
        project.has_unsent_changes = True
        project.save()
        
        modification.status = 'APPROVED'
        modification.approved_by = request.user
        modification.approved_at = timezone.now()
        modification.save()
        
        messages.success(request, 'Modification approved and applied.')
    elif action == 'reject':
        rejection_reason = request.POST.get('notes', '').strip()
        
        if not rejection_reason:
            messages.error(request, 'Rejection reason is required.')
            return redirect('project_detail', slug=modification.project.slug)
        
        modification.status = 'REJECTED'
        modification.approved_by = request.user
        modification.approved_at = timezone.now()
        modification.notes = rejection_reason
        modification.save()
        
        # Send rejection email to client with CC to admin
        try:
            send_rejection_email(modification, rejection_reason, request.user)
            messages.success(request, 'Modification rejected and client notified via email.')
        except Exception as e:
            messages.warning(request, f'Modification rejected, but email notification failed: {str(e)}')
    
    return redirect('project_detail', slug=modification.project.slug)


@login_required
def clear_notification(request, slug):
    """Clear unnotified changes flag for a project - admin only"""
    if not request.user.is_admin():
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    project = get_object_or_404(Project, slug=slug)
    project.has_unsent_changes = False
    project.admin_notified_of_changes = False
    project.save()
    return JsonResponse({'success': True, 'message': 'Notifications cleared'})


@login_required
def send_credentials(request, slug):
    """Send login credentials to client - admin only"""
    if not request.user.is_admin():
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    project = get_object_or_404(Project, slug=slug)
    client_user = project.user
    
    if not project.client_email:
        return JsonResponse({'error': 'No client email set for this project'}, status=400)
    
    # Generate a new password
    password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))
    client_user.set_password(password)
    client_user.save()
    
    # Send email with credentials
    try:
        send_mail(
            subject=f'Login Credentials for Wedding Video Portal - {project.name}',
            message=f'''
            Dear {project.client_name or client_user.get_full_name() or 'Client'},
            
            Your login credentials for the Wedding Video Portal have been created for project "{project.name}".
            
            Portal URL: {request.build_absolute_uri('/dashboard/')}
            Email: {client_user.email}
            Password: {password}
            
            Please log in using your email address and the password above. 
            We recommend changing your password after your first login.
            
            Best regards,
            Wedding Video Portal Team
            ''',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[project.client_email],
            fail_silently=False,
        )
        
        return JsonResponse({'success': True, 'message': 'Credentials sent successfully'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def change_client_data(request, slug):
    """Change client name and email for a project - admin only"""
    if not request.user.is_admin():
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    project = get_object_or_404(Project, slug=slug)
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            new_name = data.get('client_name', '').strip()
            new_email = data.get('client_email', '').strip()
            
            if not new_name or not new_email:
                return JsonResponse({'error': 'Both name and email are required'}, status=400)
            
            old_email = project.client_email
            old_name = project.client_name
            
            # If email is changing, move project to different user account
            if new_email != old_email:
                try:
                    # Find or create user for new email
                    new_user = User.objects.get(email=new_email)
                    # Update the user's name if provided
                    if new_name:
                        name_parts = new_name.split()
                        new_user.first_name = name_parts[0] if len(name_parts) > 0 else ''
                        new_user.last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''
                        new_user.save()
                        # Update name in ALL projects for this user
                        Project.objects.filter(user=new_user).update(client_name=new_name)
                        
                except User.DoesNotExist:
                    # Create new user for the new email
                    name_parts = new_name.split() if new_name else ['', '']
                    new_user = User.objects.create_user(
                        email=new_email,
                        first_name=name_parts[0] if len(name_parts) > 0 else '',
                        last_name=' '.join(name_parts[1:]) if len(name_parts) > 1 else '',
                        role='CLIENT',
                        password='temp_password_needs_reset'
                    )
                
                # Move project to new user
                project.user = new_user
                project.client_email = new_email
                project.client_name = new_name
                project.save()
                
            elif new_name != old_name:
                # Only name is changing - update all projects for this user
                name_parts = new_name.split()
                project.user.first_name = name_parts[0] if len(name_parts) > 0 else ''
                project.user.last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''
                project.user.save()
                
                # Update client_name in ALL projects for this user
                Project.objects.filter(user=project.user).update(client_name=new_name)
            
            else:
                # No changes needed
                pass
            
            return JsonResponse({
                'success': True, 
                'message': 'Client data updated successfully',
                'client_name': new_name,
                'client_email': new_email
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    # GET request - return current data
    return JsonResponse({
        'client_name': project.client_name or '',
        'client_email': project.client_email or ''
    })


@login_required
@require_http_methods(['POST'])
def update_field_order(request, slug):
    """Update the order of ceremony fields for a project"""
    project = get_object_or_404(Project, slug=slug)
    
    # Check permissions
    if not request.user.is_admin() and project.user != request.user:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    try:
        data = json.loads(request.body)
        field_order = data.get('field_order', [])
        
        if not isinstance(field_order, list):
            return JsonResponse({'error': 'field_order must be a list'}, status=400)
        
        # Validate that all fields are valid ceremony fields
        valid_fields = ['civil_union_details', 'prep', 'church', 'session', 'restaurant']
        for field in field_order:
            if field not in valid_fields:
                return JsonResponse({'error': f'Invalid field: {field}'}, status=400)
        
        # Save the field order to the project
        project.ceremony_field_order = {'order': field_order}
        project.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Field order updated successfully',
            'field_order': field_order
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def get_field_history(request, slug, field_name):
    """Get the edit history for a specific field"""
    project = get_object_or_404(Project, slug=slug)
    
    print(f"📜 Fetching history for: project={slug}, field={field_name}")
    
    # Check permissions
    if not request.user.is_admin() and project.user != request.user:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    # Get all history entries for this field
    history_entries = FieldHistory.objects.filter(
        project=project,
        field_name=field_name
    ).select_related('edited_by').order_by('-created_at')
    
    print(f"📊 Found {history_entries.count()} history entries")
    
    # Format the response
    from django.utils.timesince import timesince
    history_data = []
    for entry in history_entries:
        editor_name = entry.edited_by.get_full_name() if entry.edited_by and entry.edited_by.get_full_name() else (
            entry.edited_by.email if entry.edited_by else 'Unknown'
        )
        
        history_data.append({
            'id': entry.id,
            'old_value': entry.old_value or '',
            'new_value': entry.new_value or '',
            'edited_by': editor_name,
            'created_at': entry.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'time_ago': timesince(entry.created_at)
        })
    
    return JsonResponse({
        'success': True,
        'field_name': field_name,
        'history': history_data
    })


@login_required
def dismiss_guidance(request, slug):
    """Dismiss the current guidance message for a project"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    project = get_object_or_404(Project, slug=slug)
    
    # Only clients can dismiss guidance messages
    if request.user.is_admin() or project.user != request.user:
        return JsonResponse({'error': 'Only clients can dismiss guidance messages'}, status=403)
    
    try:
        data = json.loads(request.body)
        message_type = data.get('message_type')
        
        if not message_type:
            return JsonResponse({'error': 'Message type is required'}, status=400)
        
        # Add the message type to dismissed list if not already there
        if message_type not in project.dismissed_guidance_messages:
            project.dismissed_guidance_messages.append(message_type)
            project.save(update_fields=['dismissed_guidance_messages'])
        
        return JsonResponse({
            'success': True,
            'message': 'Guidance dismissed successfully'
        })
    
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def backup_database(request):
    """Create a database backup - admin only"""
    if not request.user.is_admin():
        messages.error(request, 'Only administrators can create backups.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        from django.core.management import call_command
        from pathlib import Path
        from datetime import datetime
        import io
        
        backup_format = request.POST.get('format', 'json')
        
        try:
            # Create backups directory if it doesn't exist
            backup_dir = Path(settings.BASE_DIR) / 'backups'
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            base_filename = f'wedding_portal_backup_{timestamp}'
            
            if backup_format == 'json':
                # JSON backup
                json_file = backup_dir / f'{base_filename}.json'
                with open(json_file, 'w', encoding='utf-8') as f:
                    call_command(
                        'dumpdata',
                        '--natural-foreign',
                        '--natural-primary',
                        '--indent', '2',
                        stdout=f,
                        exclude=['contenttypes', 'auth.permission', 'sessions.session']
                    )
                
                file_size = json_file.stat().st_size / (1024 * 1024)
                messages.success(request, f'Backup created successfully: {json_file.name} ({file_size:.2f} MB)')
                
            elif backup_format == 'sqlite':
                # SQLite file copy
                db_engine = settings.DATABASES['default']['ENGINE']
                if 'sqlite' in db_engine:
                    import shutil
                    db_path = Path(settings.DATABASES['default']['NAME'])
                    if db_path.exists():
                        sqlite_file = backup_dir / f'{base_filename}.sqlite3'
                        shutil.copy2(db_path, sqlite_file)
                        file_size = sqlite_file.stat().st_size / (1024 * 1024)
                        messages.success(request, f'Backup created successfully: {sqlite_file.name} ({file_size:.2f} MB)')
                    else:
                        messages.error(request, 'Database file not found.')
                else:
                    messages.error(request, 'SQLite backup only works with SQLite databases.')
            
            elif backup_format == 'both':
                # Both formats
                files_created = []
                
                # JSON
                json_file = backup_dir / f'{base_filename}.json'
                with open(json_file, 'w', encoding='utf-8') as f:
                    call_command(
                        'dumpdata',
                        '--natural-foreign',
                        '--natural-primary',
                        '--indent', '2',
                        stdout=f,
                        exclude=['contenttypes', 'auth.permission', 'sessions.session']
                    )
                files_created.append(json_file.name)
                
                # SQLite
                db_engine = settings.DATABASES['default']['ENGINE']
                if 'sqlite' in db_engine:
                    import shutil
                    db_path = Path(settings.DATABASES['default']['NAME'])
                    if db_path.exists():
                        sqlite_file = backup_dir / f'{base_filename}.sqlite3'
                        shutil.copy2(db_path, sqlite_file)
                        files_created.append(sqlite_file.name)
                
                messages.success(request, f'Backups created: {", ".join(files_created)}')
            
        except Exception as e:
            messages.error(request, f'Backup failed: {str(e)}')
        
        return redirect('backup_management')
    
    # GET request - show backup management page
    from pathlib import Path
    from datetime import datetime
    
    backup_dir = Path(settings.BASE_DIR) / 'backups'
    backups = []
    
    if backup_dir.exists():
        # List all backup files
        backup_files = sorted(
            backup_dir.glob('wedding_portal_backup_*'),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )
        
        for backup_file in backup_files:
            backups.append({
                'name': backup_file.name,
                'size': backup_file.stat().st_size / (1024 * 1024),  # MB
                'date': datetime.fromtimestamp(backup_file.stat().st_mtime),
                'type': backup_file.suffix[1:].upper()  # .json -> JSON
            })
    
    context = {
        'backups': backups,
        'backup_dir': str(backup_dir),
        'is_admin': True
    }
    
    return render(request, 'backup_management.html', context)


@login_required
def download_backup(request, filename):
    """Download a backup file - admin only"""
    if not request.user.is_admin():
        messages.error(request, 'Only administrators can download backups.')
        return redirect('dashboard')
    
    from pathlib import Path
    
    backup_dir = Path(settings.BASE_DIR) / 'backups'
    backup_file = backup_dir / filename
    
    # Security check: ensure file is in backups directory
    if not backup_file.resolve().is_relative_to(backup_dir.resolve()):
        messages.error(request, 'Invalid backup file.')
        return redirect('backup_management')
    
    if not backup_file.exists():
        messages.error(request, 'Backup file not found.')
        return redirect('backup_management')
    
    # Serve file
    response = FileResponse(open(backup_file, 'rb'), as_attachment=True, filename=filename)
    return response


@login_required
def delete_backup(request, filename):
    """Delete a backup file - admin only"""
    if not request.user.is_admin():
        messages.error(request, 'Only administrators can delete backups.')
        return redirect('dashboard')
    
    if request.method != 'POST':
        return redirect('backup_management')
    
    from pathlib import Path
    
    backup_dir = Path(settings.BASE_DIR) / 'backups'
    backup_file = backup_dir / filename
    
    # Security check: ensure file is in backups directory
    if not backup_file.resolve().is_relative_to(backup_dir.resolve()):
        messages.error(request, 'Invalid backup file.')
        return redirect('backup_management')
    
    if backup_file.exists():
        try:
            backup_file.unlink()
            messages.success(request, f'Backup deleted: {filename}')
        except Exception as e:
            messages.error(request, f'Failed to delete backup: {str(e)}')
    else:
        messages.error(request, 'Backup file not found.')
    
    return redirect('backup_management')
