from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpResponse, JsonResponse, FileResponse
from django.utils import timezone
from django.db.models import Q
from .models import Project, File, FileDownloadEvent, ProjectModification
from .forms import LoginForm, ProjectForm, FileUploadForm
import json


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
    
    if user.is_admin():
        # Admin sees all projects
        projects = Project.objects.filter(is_archived=False)
        pending_modifications = ProjectModification.objects.filter(status='PENDING')
        context = {
            'projects': projects,
            'pending_modifications': pending_modifications,
            'is_admin': True,
        }
    else:
        # Client sees only their projects
        projects = Project.objects.filter(user=user, is_archived=False)
        context = {
            'projects': projects,
            'is_admin': False,
        }
    
    return render(request, 'dashboard.html', context)


@login_required
def project_detail(request, pk):
    """Project detail view"""
    project = get_object_or_404(Project, pk=pk)
    
    # Check permissions
    if not request.user.is_admin() and project.user != request.user:
        messages.error(request, 'You do not have permission to view this project.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        if 'update_project' in request.POST:
            form = ProjectForm(request.POST, instance=project)
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
        form = ProjectForm(instance=project)
        file_form = FileUploadForm()
    
    files = project.files.all()
    modifications = project.modifications.filter(status='PENDING') if request.user.is_admin() else None
    
    context = {
        'project': project,
        'form': form,
        'file_form': file_form,
        'files': files,
        'modifications': modifications,
        'is_admin': request.user.is_admin(),
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
            project = form.save()
            messages.success(request, f'Project "{project.name}" created successfully.')
            return redirect('project_detail', pk=project.pk)
    else:
        form = ProjectForm()
    
    return render(request, 'project_form.html', {'form': form, 'title': 'Create Project'})


@login_required
def archive_project(request, pk):
    """Archive a project - admin only"""
    if not request.user.is_admin():
        messages.error(request, 'Only administrators can archive projects.')
        return redirect('dashboard')
    
    project = get_object_or_404(Project, pk=pk)
    project.is_archived = True
    project.save()
    messages.success(request, f'Project "{project.name}" has been archived.')
    return redirect('dashboard')


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
def notify_client(request, pk):
    """Send notification email to client - admin only"""
    if not request.user.is_admin():
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    project = get_object_or_404(Project, pk=pk)
    
    # Check if we should send notification
    if project.last_client_notification_date:
        time_since_last = timezone.now() - project.last_client_notification_date
        if time_since_last.total_seconds() < 3600:  # 1 hour cooldown
            return JsonResponse({'error': 'Please wait before sending another notification'}, status=429)
    
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
def update_project_field(request, pk):
    """Update a single project field via AJAX"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    project = get_object_or_404(Project, pk=pk)
    
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
            project.save()
            return JsonResponse({
                'success': True, 
                'message': 'Change submitted for admin approval',
                'pending_approval': True
            })
        
        # Admin changes are applied immediately
        if request.user.is_admin():
            setattr(project, field_name, field_value)
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
        setattr(project, modification.field_name, modification.new_value)
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
    
    return redirect('project_detail', pk=modification.project.pk)
