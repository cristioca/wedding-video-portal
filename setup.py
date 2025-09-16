#!/usr/bin/env python
"""
Setup script for Wedding Video Portal Django project
Run this to set up the project after cloning
"""

import os
import sys
import subprocess


def run_command(command, description):
    """Run a command and print status"""
    print(f"\n{'='*60}")
    print(f"📌 {description}")
    print(f"{'='*60}")
    try:
        subprocess.run(command, shell=True, check=True)
        print(f"✅ {description} - Success!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - Failed!")
        print(f"Error: {e}")
        return False


def main():
    print("\n" + "="*60)
    print("🎬 WEDDING VIDEO PORTAL - DJANGO SETUP")
    print("="*60)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required!")
        sys.exit(1)
    
    print(f"✅ Python {sys.version.split()[0]} detected")
    
    # Install dependencies
    if not run_command("pip install -r requirements.txt", "Installing dependencies"):
        print("\n⚠️  Failed to install dependencies. Please install manually:")
        print("   pip install -r requirements.txt")
        return
    
    # Create necessary directories
    directories = ['static', 'media', 'media/project_files']
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"✅ Created directory: {directory}")
    
    # Create .env file if it doesn't exist
    if not os.path.exists('.env'):
        with open('.env', 'w') as f:
            f.write("""# Django Settings
SECRET_KEY=django-insecure-dev-key-change-this-in-production
DEBUG=True

# Database
DATABASE_URL=sqlite:///db.sqlite3

# Email Settings (optional)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
DEFAULT_FROM_EMAIL=noreply@weddingportal.com
""")
        print("✅ Created .env file with default settings")
    
    # Run migrations
    if not run_command("python manage.py makemigrations", "Creating migrations"):
        return
    
    if not run_command("python manage.py migrate", "Applying migrations"):
        return
    
    # Seed the database
    if run_command("python manage.py seed_data", "Seeding database with sample data"):
        print("\n" + "="*60)
        print("📝 DEFAULT LOGIN CREDENTIALS:")
        print("="*60)
        print("Admin:   username: admin    | password: admin123")
        print("Client:  username: client   | password: client123")
        print("Client:  username: maria    | password: maria123")
    
    print("\n" + "="*60)
    print("🎉 SETUP COMPLETE!")
    print("="*60)
    print("\nTo start the server, run:")
    print("  python manage.py runserver")
    print("\nThen open http://localhost:8000 in your browser")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
