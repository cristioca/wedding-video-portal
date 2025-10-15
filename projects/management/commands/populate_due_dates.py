"""
Management command to populate due dates for existing projects
"""
from django.core.management.base import BaseCommand
from projects.models import Project
from dateutil.relativedelta import relativedelta


class Command(BaseCommand):
    help = 'Populate due dates for existing projects (3 months after event date)'

    def handle(self, *args, **options):
        projects_without_due_date = Project.objects.filter(due_date__isnull=True)
        count = projects_without_due_date.count()
        
        if count == 0:
            self.stdout.write(self.style.SUCCESS('All projects already have due dates set.'))
            return
        
        self.stdout.write(f'Found {count} projects without due dates. Setting defaults...')
        
        updated = 0
        for project in projects_without_due_date:
            if project.event_date:
                project.due_date = (project.event_date + relativedelta(months=3)).date()
                project.save(update_fields=['due_date'])
                updated += 1
                self.stdout.write(f'  ✓ {project.name}: Due date set to {project.due_date}')
            else:
                self.stdout.write(self.style.WARNING(f'  ⚠ {project.name}: No event date, skipping'))
        
        self.stdout.write(self.style.SUCCESS(f'\nSuccessfully updated {updated} projects.'))
