# Database Backup & Restore Guide

## Overview

The Wedding Video Portal includes comprehensive backup and restore functionality to protect your data. You can create backups through both a web interface and command-line tools.

## Web Interface (Recommended for Regular Backups)

### Accessing Backup Management
1. Log in as an admin user
2. Click **"Backup"** in the navigation menu
3. You'll see the Backup Management page

### Creating a Backup
1. Select your preferred format:
   - **JSON** (Recommended): Portable, works with any database
   - **SQLite**: Complete database file copy (SQLite only)
   - **Both**: Creates both formats
2. Click **"Create Backup Now"**
3. The backup will be created with a timestamp in the filename

### Downloading Backups
- Click the **"Download"** button next to any backup
- The file will download to your computer

### Deleting Old Backups
- Click the trash icon next to any backup
- Confirm the deletion

## Command Line Tools

### Creating Backups

#### Basic JSON Backup (Recommended)
```bash
python manage.py backup_database --format=json
```

#### SQLite File Copy
```bash
python manage.py backup_database --format=sqlite
```

#### Both Formats
```bash
python manage.py backup_database --format=both
```

#### Custom Output Directory
```bash
python manage.py backup_database --output-dir=/path/to/backups
```

#### Custom Filename
```bash
python manage.py backup_database --filename=my_backup
```

### Restoring from Backup

#### Restore from JSON (Merge with existing data)
```bash
python manage.py restore_database backups/wedding_portal_backup_20250101_120000.json
```

#### Restore with Flush (⚠️ WARNING: Deletes all existing data first)
```bash
python manage.py restore_database backups/wedding_portal_backup_20250101_120000.json --flush
```

## Backup Formats Explained

### JSON Format
- **Pros**: 
  - Portable across different database systems
  - Human-readable
  - Can be version controlled
  - Works with PostgreSQL, MySQL, SQLite, etc.
- **Cons**: 
  - Slightly larger file size
  - Slower for very large databases
- **Best for**: Regular backups, migrations, development

### SQLite Format
- **Pros**: 
  - Exact copy of database file
  - Very fast
  - Includes everything (indexes, triggers, etc.)
- **Cons**: 
  - Only works with SQLite databases
  - Binary format (not human-readable)
- **Best for**: Quick backups, disaster recovery

## Backup Storage Location

By default, backups are stored in:
```
wedding-video-portal/backups/
```

Files are named with timestamps:
```
wedding_portal_backup_20250117_143052.json
wedding_portal_backup_20250117_143052.sqlite3
```

## Best Practices

### Regular Backup Schedule
1. **Daily**: Automated JSON backups
2. **Weekly**: Download backups to external storage
3. **Before Updates**: Always backup before updating the application

### Backup Retention
- Keep at least 7 daily backups
- Keep at least 4 weekly backups
- Keep monthly backups for 1 year

### Testing Restores
- Test restore procedures in a development environment
- Verify data integrity after restore
- Document any issues or special procedures

## Automated Backups (Optional)

### Windows Task Scheduler
1. Open Task Scheduler
2. Create a new task
3. Set trigger (e.g., daily at 2 AM)
4. Set action:
   ```
   Program: python
   Arguments: manage.py backup_database --format=json
   Start in: E:\Creative Image Studio\site\2025 wedding app\wedding-video-portal
   ```

### Linux Cron Job
Add to crontab:
```bash
0 2 * * * cd /path/to/wedding-video-portal && python manage.py backup_database --format=json
```

## Disaster Recovery

### Complete System Failure
1. Install fresh Django application
2. Run migrations: `python manage.py migrate`
3. Restore from backup: `python manage.py restore_database backups/latest_backup.json --flush`
4. Restart server

### Partial Data Loss
1. Create a backup of current state first
2. Restore from backup without `--flush` to merge data
3. Review and verify data integrity

## Security Considerations

### Backup File Security
- Backups contain sensitive client data
- Store backups in secure locations
- Encrypt backups for off-site storage
- Limit access to backup files

### Recommended Encryption
```bash
# Encrypt backup
gpg -c wedding_portal_backup_20250117_143052.json

# Decrypt backup
gpg wedding_portal_backup_20250117_143052.json.gpg
```

## Troubleshooting

### Backup Fails
- Check disk space
- Verify write permissions on backups directory
- Check Django logs for errors

### Restore Fails
- Ensure backup file is not corrupted
- Verify JSON format is valid
- Check database compatibility
- Try restoring to a fresh database first

### Large Database Performance
- JSON backups may be slow for databases > 1GB
- Consider using SQLite format for faster backups
- Use `--exclude` option to skip unnecessary data

## Support

For issues or questions:
1. Check Django logs: `wedding_portal/logs/`
2. Review backup command output
3. Test in development environment first
4. Contact system administrator

## Backup Checklist

- [ ] Backups run automatically daily
- [ ] Backups are stored in secure location
- [ ] Off-site backup copy exists
- [ ] Restore procedure has been tested
- [ ] Backup retention policy is followed
- [ ] Team knows how to restore from backup
- [ ] Backup monitoring is in place
