"""
Management command to backup the database
Supports multiple formats: JSON, SQL dump, and SQLite file copy
"""
import os
import shutil
from datetime import datetime
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.conf import settings
from pathlib import Path


class Command(BaseCommand):
    help = 'Backup the database in various formats'

    def add_arguments(self, parser):
        parser.add_argument(
            '--format',
            type=str,
            default='json',
            choices=['json', 'sqlite', 'both'],
            help='Backup format: json (Django dumpdata), sqlite (file copy), or both'
        )
        parser.add_argument(
            '--output-dir',
            type=str,
            default=None,
            help='Output directory for backups (default: project_root/backups)'
        )
        parser.add_argument(
            '--filename',
            type=str,
            default=None,
            help='Custom filename (without extension)'
        )

    def handle(self, *args, **options):
        backup_format = options['format']
        output_dir = options['output_dir']
        custom_filename = options['filename']
        
        # Determine output directory
        if output_dir:
            backup_dir = Path(output_dir)
        else:
            backup_dir = Path(settings.BASE_DIR) / 'backups'
        
        # Create backup directory if it doesn't exist
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate timestamp-based filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        if custom_filename:
            base_filename = custom_filename
        else:
            base_filename = f'wedding_portal_backup_{timestamp}'
        
        self.stdout.write(self.style.SUCCESS(f'\n📦 Starting database backup...'))
        self.stdout.write(f'Backup directory: {backup_dir}\n')
        
        success_count = 0
        
        # JSON backup (Django dumpdata)
        if backup_format in ['json', 'both']:
            json_file = backup_dir / f'{base_filename}.json'
            self.stdout.write(f'Creating JSON backup: {json_file.name}...')
            try:
                with open(json_file, 'w', encoding='utf-8') as f:
                    call_command(
                        'dumpdata',
                        '--natural-foreign',
                        '--natural-primary',
                        '--indent', '2',
                        stdout=f,
                        exclude=['contenttypes', 'auth.permission', 'sessions.session']
                    )
                
                file_size = json_file.stat().st_size / (1024 * 1024)  # Size in MB
                self.stdout.write(self.style.SUCCESS(f'  ✓ JSON backup created: {file_size:.2f} MB'))
                success_count += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  ✗ JSON backup failed: {str(e)}'))
        
        # SQLite file copy (only for SQLite databases)
        if backup_format in ['sqlite', 'both']:
            db_engine = settings.DATABASES['default']['ENGINE']
            
            if 'sqlite' in db_engine:
                db_path = Path(settings.DATABASES['default']['NAME'])
                if db_path.exists():
                    sqlite_file = backup_dir / f'{base_filename}.sqlite3'
                    self.stdout.write(f'Creating SQLite backup: {sqlite_file.name}...')
                    try:
                        shutil.copy2(db_path, sqlite_file)
                        file_size = sqlite_file.stat().st_size / (1024 * 1024)  # Size in MB
                        self.stdout.write(self.style.SUCCESS(f'  ✓ SQLite backup created: {file_size:.2f} MB'))
                        success_count += 1
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'  ✗ SQLite backup failed: {str(e)}'))
                else:
                    self.stdout.write(self.style.WARNING(f'  ⚠ Database file not found: {db_path}'))
            else:
                self.stdout.write(self.style.WARNING(f'  ⚠ SQLite backup skipped (database engine: {db_engine})'))
                if backup_format == 'sqlite':
                    self.stdout.write(self.style.ERROR('  ✗ Cannot create SQLite backup for non-SQLite database'))
        
        # Summary
        self.stdout.write(self.style.SUCCESS(f'\n✅ Backup completed: {success_count} file(s) created'))
        self.stdout.write(f'Location: {backup_dir}\n')
        
        # List recent backups
        self.list_recent_backups(backup_dir)
    
    def list_recent_backups(self, backup_dir):
        """List the 5 most recent backups"""
        try:
            backups = sorted(backup_dir.glob('wedding_portal_backup_*'), key=lambda p: p.stat().st_mtime, reverse=True)
            
            if backups:
                self.stdout.write(self.style.SUCCESS('Recent backups:'))
                for i, backup in enumerate(backups[:5], 1):
                    size = backup.stat().st_size / (1024 * 1024)
                    mtime = datetime.fromtimestamp(backup.stat().st_mtime)
                    self.stdout.write(f'  {i}. {backup.name} ({size:.2f} MB) - {mtime.strftime("%Y-%m-%d %H:%M:%S")}')
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Could not list backups: {str(e)}'))
