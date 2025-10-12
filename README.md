# Wedding Video Portal - Django Edition

A professional wedding video management portal built with Django and Python for managing wedding video projects, client communications, and file deliverables.

## Features

### 🎥 Project Management
- **Multi-Type Projects**: Support for Nunta (Wedding), Botez (Baptism), and Altele (Other) event types
- **Project Dashboard**: Overview of all projects with search, filtering, and status tracking
- **Unique Project URLs**: SEO-friendly slugs with event date, type, and creation timestamp
- **Event Details**: Comprehensive project information including dates, locations, and ceremony details
- **File Management**: Secure file uploads and downloads with size tracking
- **Status Tracking**: Dual-status system (Project Status + Editing Status) with progress percentage
- **Archive System**: Soft-delete projects with dedicated archived projects view
- **Auto Project Naming**: Automatic naming based on event type and video title

### 👥 Role-Based Access Control
- **Email-Based Authentication**: Login with email instead of username
- **Admin (Videographer)**: Full access to all projects, client management, and approvals
- **Client**: Access to their own projects with modification request capabilities
- **Shared Client Accounts**: One client email can manage multiple projects (Wedding + Baptism)
- **Client Data Management**: Change client name/email with automatic account updates

### ✏️ Advanced Modification & Approval System
- **Client Requests**: Clients can request changes to project details
- **Pending Approval**: All client modifications require admin approval before being applied
- **Rejection Workflow**: Mandatory rejection reasons with automatic email notifications
- **Visual Indicators**: Clear UI showing pending, approved, and rejected changes with color coding
- **Audit Trail**: Complete history of all modifications with timestamps and user tracking
- **Admin Controls**: Approve or reject modifications with detailed notes
- **Bypass Fields**: Certain fields (filming_details, notes) apply immediately without approval
- **Field History**: Track editing history for specific fields with version control

### 📧 Notification System
- **Client Notifications**: Admin can notify clients of project updates via email
- **Admin Notifications**: Automatic email alerts when clients modify projects
- **Notification Cooldown**: 1-hour cooldown to prevent spam
- **Smart Triggers**: Only client-visible field changes trigger notifications
- **Admin-Only Fields**: Price and production notes don't trigger client notifications
- **Email Credentials**: Send login credentials to clients directly from the portal
- **Rejection Emails**: Automatic professional emails with rejection reasons (CC to admins)

### 📦 Comprehensive Package Management
- **Package Types**: 7 preset types (Clasic, Highlights, Duo, Cinema, Creative, Botez, Custom)
- **Video Format**: 4K and FullHD options
- **Camera Configuration**: 1, 2, or 3 camera setups
- **Montages**: Highlights clip, Full movie with duration options, Primary edit, Cinema style
- **Equipment Details**: Audio recorder, Stabilizer, External light tracking
- **Team Configuration**: Videographer, Operator, Assistant count
- **Delivery Medium**: Online and USB delivery options
- **Event Presence**: Detailed event coverage notes
- **Package Presets**: Quick-apply preset configurations with instant updates

### 💰 Price Management (Admin-Only)
- **Price Field**: Integer-based pricing
- **Currency Selection**: Euro or Lei with radio button selection
- **Other Details**: Additional pricing notes and terms
- **Admin-Only Visibility**: Price section only visible to administrators

### 🎬 Production Workflow
- **Tab-Based Interface**: Pre-production, Production, Download, Approval, Feedback tabs
- **Filming Details**: Client requests and videographer notes
- **Critical Production Notes**: Admin-only important production details
- **Editing Progress**: Visual progress bar with percentage tracking
- **Editing Timeline**: Visual markers (Raw Footage → Editing → Review → Delivery)
- **Production Notes**: Technical details and version history
- **Videographer Notes**: Separate notes for filming and editing phases

### 🎯 Ceremony Details Management
- **Conditional Fields**: Different fields for Wedding vs Baptism projects
- **Drag-and-Drop Reordering**: Customize field order per project
- **Main Details**: Single comprehensive field for "Altele" event type
- **Traditional Fields**: Civil Union, Preparation, Church, Photo Session, Restaurant
- **Field Persistence**: Custom order saved per project

### 🎨 Modern UI/UX
- **Responsive Design**: Works seamlessly on desktop and mobile devices
- **Bootstrap 5**: Professional gradient interface with modern dark theme
- **Multi-Language Support**: English and Romanian with easy language switching
- **Custom Modals**: Professional confirmation dialogs (no browser popups)
- **Alert System**: Styled success, error, warning, and info messages
- **Empty Field Highlighting**: Visual indicators for unfilled fields
- **Real-time Updates**: AJAX-based instant feedback without page reload
- **Editable Sections**: Toggle edit mode for different project sections
- **Client Guidance**: Context-aware guidance messages based on project status
- **Visual Status Indicators**: Color-coded badges for project and editing status

## Tech Stack

- **Backend**: Django 5.0.2, Python 3.10+
- **Database**: SQLite (development) / PostgreSQL (production ready)
- **Frontend**: Django Templates, Bootstrap 5, Custom CSS
- **Authentication**: Django built-in authentication
- **Forms**: Django Crispy Forms with Bootstrap 5
- **File Handling**: Django file upload/download system

## Database Models

### Core Models
- **User**: Custom user model with email-based authentication and role field (ADMIN/CLIENT)
  - Email as primary login (USERNAME_FIELD)
  - Auto-generated username from email
  - Custom UserManager for email-based user creation
  
- **Project**: Comprehensive wedding/event project model with 50+ fields
  - Basic: name, slug, type, status, edit_status, editing_progress
  - Client: client_name, client_email, user relationship
  - Event: event_date, city, title_video
  - Ceremony: civil_union_details, prep, church, session, restaurant, main_details
  - Package: package_type, cameras, montages, equipment, team, delivery
  - Price: price, price_currency, price_other_details (admin-only)
  - Production: filming_details, videographer notes, critical notes
  - Notifications: has_unsent_changes, last_notification_dates
  - Customization: ceremony_field_order (JSON), guidance messages
  
- **File**: Secure file storage with metadata
  - display_name, file path, size_bytes
  - uploaded_by user relationship
  - created_at timestamp
  
- **ProjectModification**: Modification tracking with approval workflow
  - field_name, old_value, new_value
  - status: PENDING, APPROVED, REJECTED, AUTO_APPLIED
  - created_by, approved_by user relationships
  - notes (for rejection reasons)
  - timestamps: created_at, approved_at
  
- **FileDownloadEvent**: Download activity tracking
  - file, project, downloaded_by relationships
  - success flag, created_at timestamp
  
- **FieldHistory**: Version control for specific fields
  - project, field_name, old_value, new_value
  - edited_by user relationship
  - created_at timestamp

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
- **Email**: `admin@admin.com`
- **Password**: `admin123`
- **Access**: All projects, client management, modification approvals, price management

### Clients
- **Email**: `client@example.com` / **Password**: `client123`
- **Email**: `maria@example.com` / **Password**: `maria123`
- **Access**: Own projects only, can request modifications, view package details

**Note**: Login uses email addresses instead of usernames.

## Usage

### For Videographers (Admin)
1. **Dashboard Overview**: View all client projects with search, filtering, and pending modification indicators
2. **Project Management**: Create, edit, and manage project details with auto-naming
3. **Modification Approval**: Review and approve/reject client change requests with mandatory rejection reasons
4. **Client Management**: Change client data, send credentials, manage multiple projects per client
5. **Package Configuration**: Set package types, pricing, equipment, and team details
6. **Price Management**: Set pricing in Euro or Lei with additional terms
7. **Production Tracking**: Manage filming/editing notes, progress, and timeline
8. **Notification System**: Notify clients of updates, view notification history
9. **File Management**: Upload final videos and track client downloads
10. **Archive System**: Archive completed projects, view archived projects separately
11. **Admin Interface**: Access Django admin at `/admin/` for advanced management

### For Clients
1. **Project Access**: View your wedding/event project details and status
2. **Request Changes**: Edit project details (requires admin approval)
3. **Package Details**: View comprehensive package configuration and delivery options
4. **Ceremony Details**: Customize and reorder ceremony detail fields
5. **File Downloads**: Access and download your completed videos
6. **Modification Tracking**: See approval status of your change requests
7. **Rejection Feedback**: Receive detailed rejection reasons for denied changes
8. **Multi-Project Access**: Manage multiple projects (Wedding + Baptism) under one account
9. **Guided Experience**: Context-aware guidance messages based on project status

## Django URLs

### Main URLs
- `/` - Home (redirects to dashboard or login)
- `/login/` - User login (email-based)
- `/logout/` - User logout
- `/dashboard/` - Main dashboard with search and filters
- `/dashboard/archived/` - Archived projects view (admin only)
- `/admin/` - Django admin interface

### Project URLs
- `/projects/<slug>/` - Project detail view (unique slug format)
- `/projects/create/` - Create new project (admin only)
- `/projects/<slug>/archive/` - Archive project (admin only)
- `/projects/<slug>/delete/` - Delete project permanently (admin only)
- `/projects/<slug>/notify/` - Send client notification (admin only)
- `/projects/<slug>/clear-notification/` - Clear notification flag (admin only)
- `/projects/<slug>/send-credentials/` - Email login credentials to client (admin only)
- `/projects/<slug>/change-client-data/` - Update client name/email (admin only)

### AJAX Endpoints
- `/projects/<slug>/update-field/` - Update single field via AJAX
- `/projects/<slug>/batch-update/` - Update multiple fields (package presets)
- `/projects/<slug>/update-field-order/` - Save ceremony field order
- `/projects/<slug>/field-history/<field_name>/` - Get field edit history
- `/projects/<slug>/dismiss-guidance/` - Dismiss guidance message
- `/projects/file/<id>/download/` - Download file with tracking
- `/projects/modification/<id>/approve/` - Approve/reject modification (admin only)

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
│   ├── models.py         # Database models (User, Project, File, etc.)
│   ├── views.py          # View functions (21 views)
│   ├── forms.py          # Django forms (Login, Project, File, User)
│   ├── admin.py          # Admin configuration
│   ├── urls.py           # App URL patterns
│   ├── templatetags/     # Custom template filters
│   │   └── project_filters.py  # attr filter for dynamic field access
│   └── management/       # Custom management commands
│       └── commands/
│           ├── seed_data.py
│           ├── populate_slugs.py
│           └── fix_client_isolation.py
├── templates/             # HTML templates
│   ├── base.html         # Base template with Bootstrap 5
│   ├── login.html        # Email-based login
│   ├── dashboard.html    # Project dashboard with search
│   ├── project_detail.html  # Main project view (3000+ lines)
│   ├── project_form.html # Project creation form
│   └── archived_projects.html  # Archived projects view
├── static/               # Static files
│   └── css/
│       └── theme.css     # Custom gradient theme
├── media/                # User uploaded files
│   └── project_files/    # Organized by date
├── requirements.txt      # Python dependencies
├── .env.example         # Environment variables template
├── setup.py             # One-click setup script
└── README.md            # This file
```

## Technical Highlights

### Backend Architecture
- **Custom User Model**: Email-based authentication with role field
- **Slug-Based URLs**: SEO-friendly project URLs with meaningful identifiers
- **AJAX-First Design**: Real-time updates without page reloads
- **Approval Workflow**: Sophisticated modification tracking system
- **Smart Notifications**: Context-aware email system with cooldown
- **Field History**: Version control for critical fields
- **JSON Fields**: Flexible storage for field ordering and guidance state

### Frontend Features
- **Bootstrap 5**: Modern responsive design with custom gradient theme
- **Multi-Language (i18n)**: English and Romanian with session-based language switching
- **SortableJS**: Drag-and-drop field reordering
- **Custom Modals**: Professional dialogs replacing browser popups
- **AJAX Forms**: Instant field updates with validation
- **Visual Feedback**: Color-coded status indicators and badges
- **Empty Field Detection**: Automatic highlighting of unfilled fields
- **Tab Navigation**: Organized workflow phases

### Security & Data Integrity
- **Role-Based Access**: Strict separation between admin and client capabilities
- **Approval System**: Client changes require admin approval
- **Admin-Only Fields**: Price and production notes hidden from clients
- **Download Tracking**: Complete audit trail of file access
- **Modification History**: Full changelog with user attribution
- **Email Verification**: Credential sending for client access

### Performance Optimizations
- **AJAX Updates**: Reduce full page reloads
- **Batch Operations**: Update multiple fields in single request
- **Efficient Queries**: Optimized database access patterns
- **File Size Tracking**: Monitor storage usage
- **Notification Cooldown**: Prevent email spam

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
# Seed database with sample data (creates admin and client accounts with projects)
python manage.py seed_data

# Populate slugs for existing projects (migration helper)
python manage.py populate_slugs

# Fix client isolation (merge projects by email - legacy)
python manage.py fix_client_isolation

# Create admin user manually
python manage.py createsuperuser
```

## Key Features Explained

### Email-Based Authentication
- Users login with email addresses instead of traditional usernames
- Usernames are auto-generated from email prefixes
- Custom UserManager handles email-based user creation
- Supports shared client accounts (one email = multiple projects)

### Unique Project URLs
- Format: `/projects/YYYY-MM-DD-type(YYYYMMDDtHHMMSS)/`
- Example: `/projects/2025-08-19-nunta(20250918-t-095748)/`
- SEO-friendly and human-readable
- Includes event date, type, and creation timestamp

### Modification Approval Workflow
- **Client Changes**: Create PENDING modifications (not applied immediately)
- **Admin Changes**: Applied immediately with AUTO_APPLIED status
- **Bypass Fields**: filming_details and notes apply immediately for all users
- **Approval**: Admin can approve (applies change) or reject (with reason)
- **Email Notifications**: Rejection emails sent to client with CC to admins

### Smart Notification System
- **Admin-Only Fields**: Changes to price, videographer notes, critical notes don't trigger client notifications
- **Client-Visible Fields**: Changes trigger "Notify Client" button
- **Cooldown Period**: 1-hour minimum between notifications to prevent spam
- **Automatic Admin Alerts**: Admins notified when clients modify projects

### Package Presets
- Quick-apply configurations for common package types
- Instant AJAX updates without page reload
- Preset values for cameras, montages, equipment based on package type
- Customizable after preset application

### Drag-and-Drop Field Ordering
- Reorder ceremony detail fields per project
- Uses SortableJS library for smooth drag-and-drop
- Custom order saved in JSON field
- Persistent across sessions

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## Project Summary

**Wedding Video Portal** is a comprehensive Django-based web application designed specifically for wedding videographers to manage client projects, track modifications, handle file deliveries, and maintain professional client communication. 

### Key Statistics
- **50+ Database Fields** per project for comprehensive tracking
- **21 View Functions** handling all application logic
- **6 Database Models** with relationships and history tracking
- **3 Event Types** supported (Wedding, Baptism, Other)
- **7 Package Presets** for quick configuration
- **Email-Based Authentication** for modern user experience
- **AJAX-First Design** for real-time updates
- **Professional UI** with Bootstrap 5 and custom gradient theme

### Perfect For
- Wedding videographers managing multiple client projects
- Video production companies needing client portals
- Event videographers tracking packages and deliverables
- Businesses requiring approval workflows for client changes
- Teams needing comprehensive project and file management

### Built With Django Best Practices
- Custom User model with email authentication
- Model managers and custom querysets
- Template tags and filters
- Management commands for automation
- AJAX endpoints for dynamic updates
- Email integration for notifications
- File upload/download with tracking
- Role-based access control
- Comprehensive admin interface

**Ready for production deployment** with PostgreSQL, Gunicorn, and proper environment configuration.
