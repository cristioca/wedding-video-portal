# Wedding Video Portal

A comprehensive client portal for wedding videographers to manage projects, track modifications, and collaborate with clients throughout the video production process.

## Features

### 🎥 Project Management
- **Project Dashboard**: Overview of all wedding projects with status tracking
- **Event Details**: Comprehensive project information including dates, locations, and requirements
- **File Management**: Secure file uploads and downloads for video deliverables
- **Status Tracking**: Real-time project status updates (Planning, In Progress, Review, Completed)

### 👥 Role-Based Access Control
- **Admin (Videographer)**: Full access to all projects and client management
- **Client**: Access only to their own projects and modification requests
- **Secure Authentication**: NextAuth.js with credential-based login

### ✏️ Modification Tracking System
- **Client Requests**: Clients can request changes to project details
- **Pending Approval**: All modifications require admin approval before being applied
- **Visual Indicators**: Clear UI showing pending, approved, and rejected changes
- **Audit Trail**: Complete history of all modifications with timestamps
- **Admin Controls**: Approve or reject modifications with optional notes

### 🎨 Modern UI/UX
- **Responsive Design**: Works seamlessly on desktop and mobile devices
- **Dark Theme**: Professional dark interface optimized for video professionals
- **Intuitive Navigation**: Tab-based project views for easy information access
- **Real-time Updates**: Instant feedback on actions and status changes

## Tech Stack

- **Frontend**: Next.js 14, React 18, TypeScript
- **Backend**: Next.js API Routes, Prisma ORM
- **Database**: SQLite (easily configurable for PostgreSQL/MySQL)
- **Authentication**: NextAuth.js
- **Styling**: Tailwind CSS
- **File Handling**: Built-in file upload/download system

## Database Schema

### Core Models
- **User**: Admin and client user management with role-based access
- **Project**: Wedding project details with comprehensive event information
- **File**: Secure file storage and download tracking
- **ProjectModification**: Modification requests with approval workflow

## Quick Start

### Prerequisites
- Node.js 18+ 
- npm or yarn

### Installation

1. **Clone and install dependencies**
   ```bash
   git clone <repository-url>
   cd wedding-video-portal
   npm install
   ```

2. **Environment setup**
   ```bash
   cp .env.example .env
   ```
   Update `.env` with:
   - `DATABASE_URL`: Your database connection string
   - `NEXTAUTH_SECRET`: Random secret for NextAuth.js
   - `NEXTAUTH_URL`: Your application URL (http://localhost:3000 for development)

3. **Database setup**
   ```bash
   npx prisma db push
   npx prisma generate
   npm run db:seed
   ```

4. **Start development server**
   ```bash
   npm run dev
   ```

5. **Access the application**
   Open [http://localhost:3000](http://localhost:3000)

## Demo Accounts

### Admin (Videographer)
- **Email**: `admin@admin.com`
- **Password**: `adminadmin`
- **Access**: All projects, client management, modification approvals

### Client
- **Email**: `client@client.com`  
- **Password**: `clientclient`
- **Access**: Own projects only, can request modifications

## Usage

### For Videographers (Admin)
1. **Dashboard Overview**: View all client projects with pending modification indicators
2. **Project Management**: Access detailed project information and files
3. **Modification Approval**: Review and approve/reject client change requests
4. **File Management**: Upload final videos and track client downloads

### For Clients
1. **Project Access**: View your wedding project details and status
2. **Request Changes**: Edit project details (requires admin approval)
3. **File Downloads**: Access and download your completed videos
4. **Real-time Updates**: See approval status of your modification requests

## API Endpoints

### Authentication
- `POST /api/auth/signin` - User login
- `POST /api/auth/signout` - User logout

### Projects
- `GET /api/projects` - List projects (filtered by user role)
- `GET /api/projects/[id]` - Get project details
- `PATCH /api/projects/[id]/update` - Update project (creates modification request)

### Modifications
- `GET /api/projects/[id]/modifications` - Get project modifications
- `PATCH /api/projects/[id]/modifications` - Approve/reject modifications (admin only)

### Files
- `POST /api/files/upload` - Upload files
- `GET /api/files/[id]/download` - Download files (with access control)

## Development

### Database Management
```bash
# View database in browser
npm run db:studio

# Reset database
npx prisma db push --force-reset
npm run db:seed

# Generate Prisma client after schema changes
npx prisma generate
```

### Project Structure
```
├── app/                    # Next.js 13+ app directory
│   ├── api/               # API routes
│   ├── dashboard/         # Main dashboard pages
│   ├── login/            # Authentication pages
│   └── globals.css       # Global styles
├── components/            # Reusable React components
├── lib/                  # Utility functions and configurations
├── prisma/               # Database schema and migrations
└── public/               # Static assets
```

## Deployment

### Production Build
```bash
npm run build
npm start
```

### Environment Variables (Production)
- Set `DATABASE_URL` to your production database
- Generate secure `NEXTAUTH_SECRET`
- Update `NEXTAUTH_URL` to your domain

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
