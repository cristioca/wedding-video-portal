from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpResponse, JsonResponse, FileResponse
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from datetime import datetime
from django.db.models import Q
from .models import Project, File, FileDownloadEvent, ProjectModification, User
from .forms import LoginForm, ProjectForm, ProjectDetailForm, FileUploadForm
import json
import secrets
import string


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
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
                return redirect('dashboard')
            else:
                messages.error(request, 'Invalid username or password.')
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
    sort_by = request.GET.get('sort', 'newest')  # Default sort by newest first
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
            form = ProjectDetailForm(request.POST, instance=project)
            if form.is_valid():
                # Track modifications if client is editing
                if request.user.is_client():
                    for field in form.changed_data:
                        old_value = str(getattr(project, field))
                        new_value = str(form.cleaned_data[field])
                        ProjectModification.objects.create(
                            project=project,
                            field_name=field,
                            old_value=old_value,
                            new_value=new_value,
                            created_by=request.user,
                            status='PENDING' if not request.user.is_admin() else 'AUTO_APPLIED'
                        )
                    
                    if form.changed_data:
                        project.admin_notified_of_changes = True
                        messages.info(request, 'Your changes have been submitted for admin approval.')
                
                # Admin changes are applied immediately
                if request.user.is_admin():
                    form.save()
                    messages.success(request, 'Project updated successfully.')
                
                return redirect('project_detail', pk=project.pk)
        
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
    
    context = {
        'project': project,
        'form': form,
        'file_form': file_form,
        'files': files,
        'modifications': modifications,
        'is_admin': request.user.is_admin(),
        'ceremony_fields': ceremony_fields,
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
            project.status = 'Planning'
            project.edit_status = 'Pending'
            
            # Handle client user creation/assignment
            client_email = form.cleaned_data.get('client_email')
            client_name = form.cleaned_data.get('client_name')
            
            if client_email:
                try:
                    client_user = User.objects.get(email=client_email)
                    # Update name if different
                    if client_name and client_user.first_name != client_name.split()[0]:
                        name_parts = client_name.split()
                        client_user.first_name = name_parts[0] if len(name_parts) > 0 else ''
                        client_user.last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''
                        client_user.save()
                except User.DoesNotExist:
                    # Create new client user with temporary username
                    username = client_email.split('@')[0]
                    counter = 1
                    original_username = username
                    while User.objects.filter(username=username).exists():
                        username = f"{original_username}{counter}"
                        counter += 1
                    
                    name_parts = client_name.split() if client_name else ['', '']
                    client_user = User.objects.create_user(
                        username=username,
                        email=client_email,
                        first_name=name_parts[0] if len(name_parts) > 0 else '',
                        last_name=' '.join(name_parts[1:]) if len(name_parts) > 1 else '',
                        role='CLIENT',
                        password='temp_password_needs_reset'
                    )
                project.user = client_user
            else:
                # Create a default client user if no email provided
                client_user = User.objects.create_user(
                    username=f"client_{timezone.now().strftime('%Y%m%d_%H%M%S')}",
                    email='',
                    first_name=client_name.split()[0] if client_name else 'Client',
                    last_name=' '.join(client_name.split()[1:]) if client_name and len(client_name.split()) > 1 else '',
                    role='CLIENT',
                    password='temp_password_needs_reset'
                )
                project.user = client_user
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
        if hasattr(field, 'choices') and field.choices:
            # Validate choice field
            valid_choices = [choice[0] for choice in field.choices]
            if field_value not in valid_choices:
                return JsonResponse({'error': 'Invalid choice'}, status=400)
        
        # Track modifications if client is editing
        if request.user.is_client():
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
            return JsonResponse({
                'success': True, 
                'message': 'Change submitted for admin approval',
                'pending_approval': True
            })
        
        # Admin changes are applied immediately
        if request.user.is_admin():
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
            
            # If title_video is updated, also update the project name
            if field_name == 'title_video' and field_value:
                project.name = field_value
            
            # Mark that there are changes not yet notified to the client
            project.has_unsent_changes = True
            project.save()
            
            # Create auto-applied modification record
            ProjectModification.objects.create(
                project=project,
                field_name=field_name,
                old_value=old_value,
                new_value=str(field_value),
                created_by=request.user,
                status='AUTO_APPLIED'
            )
            
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
        modification.status = 'REJECTED'
        modification.approved_by = request.user
        modification.approved_at = timezone.now()
        modification.notes = request.POST.get('notes', '')
        modification.save()
        
        messages.info(request, 'Modification rejected.')
    
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
            Dear {project.client_name or client_user.get_full_name() or client_user.username},
            
            Your login credentials for the Wedding Video Portal have been created for project "{project.name}".
            
            Portal URL: {request.build_absolute_uri('/dashboard/')}
            Username: {client_user.username}
            Password: {password}
            
            Please log in and change your password after your first login.
            
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
            
            # Update project fields
            project.client_name = new_name
            project.client_email = new_email
            
            # Update user fields
            name_parts = new_name.split() if new_name else ['', '']
            project.user.first_name = name_parts[0] if len(name_parts) > 0 else ''
            project.user.last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''
            project.user.email = new_email
            project.user.save()
            
            project.save()
            
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
