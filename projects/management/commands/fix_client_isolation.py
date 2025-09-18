from django.core.management.base import BaseCommand
from projects.models import Project, User
from collections import defaultdict


class Command(BaseCommand):
    help = 'Merge projects by client email - clients with same email share user account'

    def handle(self, *args, **options):
        # Group projects by client_email
        email_projects = defaultdict(list)
        
        for project in Project.objects.all():
            if project.client_email:
                email_projects[project.client_email].append(project)
        
        merged_count = 0
        
        for client_email, projects in email_projects.items():
            if len(projects) <= 1:
                continue  # Skip if only one project for this email
                
            self.stdout.write(f'Processing {len(projects)} projects for email: {client_email}')
            
            # Find or create the main user for this email
            try:
                main_user = User.objects.get(email=client_email)
            except User.DoesNotExist:
                # Create user based on first project's data
                first_project = projects[0]
                name_parts = first_project.client_name.split() if first_project.client_name else ['', '']
                main_user = User.objects.create_user(
                    email=client_email,
                    first_name=name_parts[0] if len(name_parts) > 0 else '',
                    last_name=' '.join(name_parts[1:]) if len(name_parts) > 1 else '',
                    role='CLIENT',
                    password='temp_password_needs_reset'
                )
                self.stdout.write(f'Created main user: {client_email}')
            
            # Move all projects to the main user
            for project in projects:
                if project.user != main_user:
                    old_user = project.user
                    project.user = main_user
                    project.save()
                    
                    # Delete the old user if it has no more projects
                    if not Project.objects.filter(user=old_user).exists():
                        old_user.delete()
                        self.stdout.write(f'Deleted unused user: {old_user.email}')
                    
                    merged_count += 1
                    self.stdout.write(f'Moved project "{project.name}" to {client_email}')
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully merged {merged_count} projects by client email.')
        )
