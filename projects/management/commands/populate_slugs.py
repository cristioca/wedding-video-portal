from django.core.management.base import BaseCommand
from projects.models import Project


class Command(BaseCommand):
    help = 'Populate slug fields for existing projects'

    def handle(self, *args, **options):
        projects_updated = 0
        
        for project in Project.objects.filter(slug__isnull=True):
            # Generate slug based on event date, type, and creation time
            event_date_str = project.event_date.strftime('%Y-%m-%d')
            creation_date_str = project.created_at.strftime('%Y%m%d-t-%H%M%S')
            type_slug = project.type.lower()
            
            # Create the slug
            slug_base = f"{event_date_str}-{type_slug}({creation_date_str})"
            
            # Ensure uniqueness by adding a counter if needed
            slug = slug_base
            counter = 1
            while Project.objects.filter(slug=slug).exclude(pk=project.pk).exists():
                slug = f"{slug_base}-{counter}"
                counter += 1
            
            project.slug = slug
            project.save()
            projects_updated += 1
            
            self.stdout.write(
                self.style.SUCCESS(f'Updated project "{project.name}" with slug: {slug}')
            )
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully updated {projects_updated} projects with slugs.')
        )
