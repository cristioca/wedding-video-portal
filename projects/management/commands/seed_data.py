from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from projects.models import Project

User = get_user_model()


class Command(BaseCommand):
    help = 'Seeds the database with initial data'

    def handle(self, *args, **options):
        self.stdout.write('Seeding database...')
        
        # Create admin user
        admin, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@admin.com',
                'first_name': 'Admin',
                'last_name': 'User',
                'role': 'ADMIN',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created:
            admin.set_password('admin123')
            admin.save()
            self.stdout.write(self.style.SUCCESS(f'Created admin user: admin'))
        
        # Create client users
        client1, created = User.objects.get_or_create(
            username='client',
            defaults={
                'email': 'client@example.com',
                'first_name': 'John',
                'last_name': 'Doe',
                'role': 'CLIENT',
            }
        )
        if created:
            client1.set_password('client123')
            client1.save()
            self.stdout.write(self.style.SUCCESS(f'Created client user: client'))
        
        client2, created = User.objects.get_or_create(
            username='maria',
            defaults={
                'email': 'maria@example.com',
                'first_name': 'Maria',
                'last_name': 'Popescu',
                'role': 'CLIENT',
            }
        )
        if created:
            client2.set_password('maria123')
            client2.save()
            self.stdout.write(self.style.SUCCESS(f'Created client user: maria'))
        
        # Create sample projects
        projects_data = [
            {
                'name': 'Maria & Ion Wedding',
                'user': client1,
                'type': 'NUNTA',
                'status': 'Editing',
                'edit_status': 'In Progress',
                'event_date': timezone.now() - timedelta(days=30),
                'city': 'Bucharest',
                'title_video': 'Maria & Ion - Love Story',
                'civil_union_details': 'Civil ceremony at City Hall, 10:00 AM',
                'prep': 'Bride preparation at Hotel Marriott, Groom at home',
                'church': 'Orthodox Church, 2:00 PM ceremony',
                'session': 'Photo session in Herastrau Park',
                'restaurant': 'Grand Ballroom, 7:00 PM reception',
                'details_extra': '300 guests, traditional Romanian wedding',
                'editing_preferences': 'Classic style, 20-minute highlight video',
                'notes': 'Client requested extra focus on dance moments',
            },
            {
                'name': 'Ana & Mihai Baptism',
                'user': client2,
                'type': 'BOTEZ',
                'status': 'Planning',
                'edit_status': 'Pending',
                'event_date': timezone.now() + timedelta(days=15),
                'city': 'Cluj-Napoca',
                'title_video': 'Little Angel - Ana\'s Baptism',
                'church': 'Catholic Church, 11:00 AM',
                'restaurant': 'Restaurant Select, 1:00 PM',
                'details_extra': '50 guests, intimate celebration',
                'editing_preferences': 'Soft, warm colors, 10-minute video',
            },
            {
                'name': 'Elena & George Wedding',
                'user': client2,
                'type': 'NUNTA',
                'status': 'Completed',
                'edit_status': 'Completed',
                'event_date': timezone.now() - timedelta(days=90),
                'city': 'Timisoara',
                'title_video': 'Forever Together',
                'civil_union_details': 'Already married, religious ceremony only',
                'prep': 'Both at bride\'s parents house',
                'church': 'Baptist Church, 4:00 PM',
                'session': 'City center and Roses Park',
                'restaurant': 'Casa Bunicii, 6:00 PM',
                'details_extra': '150 guests, outdoor reception',
                'editing_preferences': 'Modern, dynamic editing, drone shots',
                'notes': 'Final video delivered, client very satisfied',
            },
        ]
        
        for project_data in projects_data:
            project, created = Project.objects.get_or_create(
                name=project_data['name'],
                defaults=project_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created project: {project.name}'))
        
        self.stdout.write(self.style.SUCCESS('Database seeding completed!'))
