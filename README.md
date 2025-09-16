# Wedding Video Portal - Django Edition

A professional wedding video management portal built with Django and Python for managing wedding video projects, client communications, and file deliverables.

## Features

### 🎥 Project Management
- **Project Dashboard**: Overview of all wedding projects with status tracking
- **Event Details**: Comprehensive project information including dates, locations, and requirements
- **File Management**: Secure file uploads and downloads for video deliverables
- **Status Tracking**: Real-time project status updates (Planning, Filming, Editing, Completed)

### 👥 Role-Based Access Control
- **Admin (Videographer)**: Full access to all projects and client management
- **Client**: Access only to their own projects and modification requests
- **Django Authentication**: Built-in secure user authentication system

### ✏️ Modification Tracking System
- **Client Requests**: Clients can request changes to project details
- **Pending Approval**: All modifications require admin approval before being applied
- **Visual Indicators**: Clear UI showing pending, approved, and rejected changes
- **Audit Trail**: Complete history of all modifications with timestamps
- **Admin Controls**: Approve or reject modifications with optional notes

### 🎨 Modern UI/UX
- **Responsive Design**: Works seamlessly on desktop and mobile devices
- **Bootstrap 5**: Professional gradient interface with modern styling
- **Intuitive Navigation**: Clean dashboard and project detail views
- **Real-time Updates**: Instant feedback on actions and status changes

## Tech Stack

- **Backend**: Django 5.0.2, Python 3.10+
- **Database**: SQLite (development) / PostgreSQL (production ready)
- **Frontend**: Django Templates, Bootstrap 5, Custom CSS
- **Authentication**: Django built-in authentication
- **Forms**: Django Crispy Forms with Bootstrap 5
- **File Handling**: Django file upload/download system

## Database Models

### Core Models
- **User**: Custom user model with role-based access (ADMIN/CLIENT)
- **Project**: Wedding project details with comprehensive event information
- **File**: Secure file storage and download tracking with size management
- **ProjectModification**: Modification requests with approval workflow
- **FileDownloadEvent**: Download activity tracking and analytics

## Quick Start

### Prerequisites
- Python 3.10+
- pip (Python package manager)

### Installation

1. **Clone and setup virtual environment**
   ```bash
   git clone <repository-url>
   cd wedding-video-portal
   python -m venv venv
   
   # On Windows:
   venv\Scripts\activate
   
   # On macOS/Linux:
   source venv/bin/activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment setup**
   ```bash
   cp .env.example .env
   ```
   Update `.env` with:
   - `SECRET_KEY`: Django secret key
   - `DEBUG`: Set to True for development
   - `DATABASE_URL`: Database connection string

4. **Database setup**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   python manage.py seed_data
   ```

5. **Start development server**
   ```bash
   python manage.py runserver
   ```

6. **Access the application**
   Open [http://localhost:8000](http://localhost:8000)

## Demo Accounts

### Admin (Videographer)
- **Username**: `admin`
- **Password**: `admin123`
- **Access**: All projects, client management, modification approvals

### Clients
- **Username**: `client` / **Password**: `client123`
- **Username**: `maria` / **Password**: `maria123`
- **Access**: Own projects only, can request modifications

## Usage

### For Videographers (Admin)
1. **Dashboard Overview**: View all client projects with pending modification indicators
2. **Project Management**: Create, edit, and manage project details
3. **Modification Approval**: Review and approve/reject client change requests
4. **File Management**: Upload final videos and track client downloads
5. **Admin Interface**: Access Django admin at `/admin/` for advanced management

### For Clients
1. **Project Access**: View your wedding project details and status
2. **Request Changes**: Edit project details (requires admin approval)
3. **File Downloads**: Access and download your completed videos
4. **Real-time Updates**: See approval status of your modification requests

## Django URLs

### Main URLs
- `/` - Home (redirects to dashboard or login)
- `/login/` - User login
- `/logout/` - User logout
- `/dashboard/` - Main dashboard
- `/admin/` - Django admin interface

### Project URLs
- `/projects/<id>/` - Project detail view
- `/projects/create/` - Create new project (admin only)
- `/projects/<id>/archive/` - Archive project (admin only)
- `/projects/file/<id>/download/` - Download file
- `/projects/<id>/notify/` - Send client notification (admin only)

## Development

### Database Management
```bash
# Create new migrations after model changes
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Seed database with sample data
python manage.py seed_data

# Access Django shell
python manage.py shell
```

### Project Structure
```
wedding-video-portal/
├── wedding_portal/         # Django project settings
│   ├── settings.py        # Main configuration
│   ├── urls.py           # URL routing
│   └── wsgi.py           # WSGI configuration
├── projects/              # Main Django app
│   ├── models.py         # Database models
│   ├── views.py          # View functions
│   ├── forms.py          # Django forms
│   ├── admin.py          # Admin configuration
│   ├── urls.py           # App URL patterns
│   └── management/       # Custom management commands
├── templates/             # HTML templates
├── static/               # Static files (CSS, JS, images)
├── media/                # User uploaded files
└── requirements.txt      # Python dependencies
```

## Deployment

### Production Setup
```bash
# Install production dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic

# Run with production server (e.g., Gunicorn)
pip install gunicorn
gunicorn wedding_portal.wsgi:application
```

### Environment Variables (Production)
- Set `DEBUG=False`
- Generate secure `SECRET_KEY`
- Configure production database URL
- Set up email backend for notifications

## Management Commands

### Custom Commands
```bash
# Seed database with sample data
python manage.py seed_data

# Create admin user (if not using seed_data)
python manage.py createsuperuser
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
