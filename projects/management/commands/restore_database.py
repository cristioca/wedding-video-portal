"""
Management command to restore the database from a backup
"""
import os
from pathlib import Path
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.conf import settings


class Command(BaseCommand):
    help = 'Restore the database from a JSON backup file'

    def add_arguments(self, parser):
        parser.add_argument(
            'backup_file',
            type=str,
            help='Path to the backup file (JSON format)'
        )
        parser.add_argument(
            '--flush',
            action='store_true',
            help='Flush the database before restoring (WARNING: deletes all data)'
        )

    def handle(self, *args, **options):
        backup_file = Path(options['backup_file'])
        should_flush = options['flush']
        
        # Validate backup file exists
        if not backup_file.exists():
            self.stdout.write(self.style.ERROR(f'✗ Backup file not found: {backup_file}'))
            return
        
        if not backup_file.suffix == '.json':
            self.stdout.write(self.style.ERROR('✗ Only JSON backup files are supported for restore'))
            return
        
        self.stdout.write(self.style.WARNING('\n⚠️  DATABASE RESTORE WARNING ⚠️'))
        self.stdout.write(self.style.WARNING('This operation will modify your database.'))
        
        if should_flush:
            self.stdout.write(self.style.ERROR('\n🔥 FLUSH MODE: All existing data will be DELETED first!'))
        
        self.stdout.write(f'\nBackup file: {backup_file}')
        self.stdout.write(f'File size: {backup_file.stat().st_size / (1024 * 1024):.2f} MB\n')
        
        # Confirmation prompt
        confirm = input('Type "yes" to proceed with restore: ')
        if confirm.lower() != 'yes':
            self.stdout.write(self.style.WARNING('Restore cancelled.'))
            return
        
        try:
            # Flush database if requested
            if should_flush:
                self.stdout.write('\n🔥 Flushing database...')
                call_command('flush', '--no-input')
                self.stdout.write(self.style.SUCCESS('  ✓ Database flushed'))
            
            # Load data from backup
            self.stdout.write('\n📥 Restoring data from backup...')
            call_command('loaddata', str(backup_file))
            
            self.stdout.write(self.style.SUCCESS('\n✅ Database restored successfully!'))
            self.stdout.write('\nRecommendation: Restart the Django server to ensure all changes take effect.\n')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\n✗ Restore failed: {str(e)}'))
            self.stdout.write(self.style.WARNING('\nThe database may be in an inconsistent state.'))
            self.stdout.write('Consider restoring from a different backup or checking the error above.\n')
