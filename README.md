# Internship Portal - Complete Project Analysis & User Manual

## Overview

The **Internship Portal** is a comprehensive Django-based web application designed for educational institutions (specifically VelTech University) to manage student internships, company partnerships, and administrative workflows. This system streamlines the entire internship lifecycle from application to attendance tracking.

## Technology Stack & Dependencies

### Core Framework
- **Backend**: Django 5.2.5 (Python 3.11)
- **Database**: PostgreSQL (via psycopg2-binary)
- **Web Server**: Gunicorn with gevent workers
- **Containerization**: Docker
- **Static Files**: Whitenoise with compression

### Key Integrations
- **Authentication**: Django Allauth (Google OAuth2)
- **Admin Interface**: Django Jazzmin + Django Admin Interface
- **File Storage**: Cloudinary (PDF document storage)
- **Email**: SMTP (Gmail)
- **Spreadsheet Sync**: Google Sheets API
- **Data Export**: Django Import/Export
- **Rate Limiting**: Django Ratelimit
- **Scheduling**: Django Crontab

### Frontend Technologies
- **CSS Frameworks**: Bootstrap 5.3, Font Awesome
- **Icons**: Bootstrap Icons, Font Awesome
- **Responsive Design**: Mobile-first approach
- **JavaScript**: Vanilla JS for form interactions

## Architecture

### Database Schema

```mermaid
erDiagram
    Company ||--o{ Student : "offers_internship"
    Company ||--o{ Attendance : "tracks"
    Student ||--o{ Attendance : "records"
    Student ||--o{ InternshipApplication : "submits"
    
    Company {
        uuid uid PK
        string name
        string cgpa
        string fees
        string duration
        string domain
        text description
        text skill_required
        string location
        integer vacancy
        boolean active
        string username
        string password
    }
    
    Student {
        integer id PK
        string name
        string roll_number UK
        string mobile_number
        string department
        string fee
        string house
        cloudinary_field approval_letter
        boolean approval_letter_got
        cloudinary_field undertaking_letter
        boolean undertaking_letter_got
        cloudinary_field bonafide_letter
        boolean bonafide_letter_got
        foreign_key applied_company FK
    }
    
    InternshipApplication {
        integer id PK
        email email
        string student_name
        string vtu_number
        string department
        string contact_number
        string industry_name
        string industry_location
        string domain_of_work
        string industry_category
        string industry_website
        email industry_email
        string industry_phone_number
        string referal_person_name
        string referal_person_designation
        email referal_person_email
        string referal_person_phone_number
        string stipend_provided
        string stipend_amount
        string fees_required
        string fees_amount
        string application_approved
        text approval_message
        datetime submitted_at
        string student_2_to_10
        string vtu_number_2_to_10
        string contact_number_stu_2_to_10
        string department_stu_2_to_10
    }
    
    Attendance {
        integer id PK
        foreign_key student FK
        string vtu_number
        foreign_key company FK
        date date
        string status
    }
    
    Announcement {
        integer id PK
        text message1
        boolean is_message1_active
        string message1_color
        text message2
        boolean is_message2_active
        string message2_color
    }
    
    SiteSetting {
        integer id PK
        boolean maintenance_mode
        boolean active_approval_letter
        boolean active_undertaking_letter
        boolean active_bonafide_letter
    }
    
    UserReport {
        integer id PK
        string name
        string roll_number
        email email
        text problem
        datetime submitted_at
    }
    
    StudentReport {
        integer id PK
        string roll_number UK
        string report_status
    }
    
    downloadable_files {
        integer id PK
        string file_name
        url file_link
    }
```

### Application Flow Architecture

```mermaid
flowchart TD
    A[Student Login via Google OAuth] --> B{Authentication Type}
    B -->|VTU Email| C[Dashboard Access]
    B -->|Non-VTU Email| D[Access Denied]
    
    C --> E[View Available Companies]
    C --> F[Check Application Status]
    C --> G[External Company Application]
    C --> H[Support/Report Issues]
    C --> I[Upload Documents]
    
    E --> J[Apply to Company]
    J --> K{Vacancy Available?}
    K -->|Yes| L[Create Application]
    K -->|No| M[Show Error Message]
    
    G --> N[OTP Verification]
    N --> O[External Application Form]
    O --> P[Admin Review Required]
    
    Q[Company Login] --> R[Attendance Management]
    R --> S[Mark Daily Attendance]
    
    T[Department Login] --> U[Department Dashboard]
    U --> V[View Student Analytics]
    U --> W[Document Status Tracking]
    
    X[Admin Panel] --> Y[Manage Companies]
    X --> Z[Manage Students]
    X --> AA[Review Applications]
    X --> BB[System Settings]
```

### Component Architecture

```mermaid
graph TB
    subgraph "Frontend Layer"
        A[Base Template]
        B[Navigation Component]
        C[Form Components]
        D[Dashboard Views]
        E[Error Pages]
    end
    
    subgraph "Middleware Layer"
        F[Authentication Middleware]
        G[Domain Restriction]
        H[Maintenance Mode]
        I[Session Management]
        J[Rate Limiting]
    end
    
    subgraph "Views Layer"
        K[Student Views]
        L[Company Views]
        M[Department Views]
        N[Admin Views]
        O[API Views]
    end
    
    subgraph "Business Logic"
        P[Application Logic]
        Q[Attendance Logic]
        R[Document Management]
        S[Email Notifications]
        T[Google Sheets Sync]
    end
    
    subgraph "Data Layer"
        U[Django Models]
        V[PostgreSQL Database]
        W[Cloudinary Storage]
        X[Session Store]
    end
    
    A --> F
    F --> K
    K --> P
    P --> U
    U --> V
```

## User Roles & Access Control

### Student Role
**Access Requirements:**
- Must use VTU email (@veltech.edu.in)
- Google OAuth2 authentication required
- Automatic role assignment based on email domain

**Permissions:**
- View available internship companies
- Apply to internal companies (limited to one)
- Submit external company applications
- Check application status
- Upload required documents (approval letter, undertaking, bonafide)
- Submit support reports
- View personal dashboard and attendance records

### Company Role
**Access Requirements:**
- Username/password authentication
- Credentials auto-generated during company creation
- Session-based authentication (no persistent login)

**Permissions:**
- Mark daily attendance for assigned students
- View student list for their company
- Access attendance management interface

### Department Role
**Access Requirements:**
- Department-specific username/password
- Manual credential setup required
- Department-specific access control

**Permissions:**
- View all students from their department
- Monitor document submission status
- Track attendance analytics
- View department-wide statistics

### Administrator Role
**Access Requirements:**
- Django superuser privileges
- Full system access

**Permissions:**
- Complete CRUD operations on all models
- Manage companies, students, applications
- Configure site settings and announcements
- Export data to CSV
- Import student data via CSV
- Review and approve/reject external applications
- Manage downloadable files

## Feature Documentation

### Authentication System

#### Google OAuth2 Integration
```python
# Configuration in settings.py
SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "SCOPE": ["profile", "email"],
        "AUTH_PARAMS": {"access_type": "online"},
        "APP": {
            "client_id": os.getenv("SOCIAL_AUTH_GOOGLE_OAUTH2_KEY"),
            "secret": os.getenv("SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET"),
        }
    }
}
```

**Email Domain Restriction:**
- Only @veltech.edu.in emails allowed
- Automatic role assignment based on email prefix
- VTU number extraction from email (vtu24875@veltech.edu.in → 24875)

#### OTP-Based Verification
For external applications and support system:
- 6-digit OTP generation
- Email delivery via SMTP
- Session-based verification
- Bypass option for specific test accounts

### Company Management

#### Company Registration
**Automatic Credential Generation:**
```python
def save(self, *args, **kwargs):
    if not self.username:
        base_username = slugify(self.name).replace("-", "")[:10].lower()
        count = Company.objects.filter(username__startswith=base_username).count()
        self.username = f"{base_username}{count+1}" if count else base_username
    
    if not self.password:
        prefix = self.username[:4]
        year = "2025"
        count = Company.objects.filter(username__startswith=prefix).count()
        self.password = f"{prefix}{year}{count+1}"
```

**Company Features:**
- Vacancy management with atomic operations
- Active/inactive status control
- Automatic credential generation
- Domain and skill requirements specification
- Location and fee information

### Application System

#### Internal Company Applications
**Process Flow:**
1. Student browses active companies with vacancies
2. Single application per student (prevents multiple enrollments)
3. Atomic transaction ensures data consistency
4. Vacancy count decreases automatically
5. Immediate enrollment confirmation

**Validation Rules:**
- No duplicate applications
- Vacancy availability check
- Blacklist verification (blocked students)
- External application conflict check

#### External Company Applications
**Multi-step Process:**
1. Email-based OTP verification
2. Comprehensive application form (up to 10 students)
3. Industry and referral person details
4. Stipend and fee information
5. Admin review and approval workflow

**Group Application Support:**
```python
# Supports up to 10 students in single application
for i in range(2, 11):
    field_name = f"vtu_number_{i}"
    student_field = f"student_{i}"
    contact_field = f"contact_number_stu_{i}"
    dept_field = f"department_stu_{i}"
```

### Document Management

#### Cloudinary Integration
**Document Types:**
- Approval Letter (Department approval)
- Undertaking Letter (Student commitment)
- Bonafide Certificate (Institution verification)

**Upload Configuration:**
```python
approval_letter = CloudinaryField(
    resource_type="raw",
    folder="APPROVAL_LETTERS",
    public_id=lambda instance: f"{instance.name}_{instance.roll_number}_approval",
    blank=True, null=True
)
```

**Validation Rules:**
- Maximum file size: 2MB
- Format restriction: PDF only
- MIME type verification
- Automatic file naming convention

### Attendance System

#### Company Portal
**Features:**
- Daily attendance marking
- Student list filtering
- Date-specific attendance records
- Bulk attendance submission
- Attendance history view

**Data Model:**
```python
class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    status = models.CharField(choices=[("Present", "Present"), ("Absent", "Absent")])
    
    class Meta:
        unique_together = ("student", "company", "date")
```

#### Department Analytics
**Dashboard Features:**
- Department-wise student listing
- Attendance percentage calculation
- Document submission tracking
- Performance analytics
- Export capabilities

### Google Sheets Integration

#### Automated Synchronization
**Configuration:**
```python
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_info(settings.GOOGLE_CONFIG, scopes=SCOPES)
client = gspread.authorize(creds)
sheet = client.open_by_key(settings.GOOGLE_SHEET_ID).sheet1
```

**Sync Features:**
- Automatic data synchronization
- Cron job scheduling
- Error handling and recovery
- Real-time data updates

### Admin Panel Features

#### Django Jazzmin Customization
**Interface Enhancements:**
- Custom branding and logos
- Organized navigation menu
- Role-based menu visibility
- Performance dashboard
- Quick action buttons

**Data Management:**
- CSV import/export functionality
- Bulk operations
- Advanced filtering and search
- Relationship management
- Audit trail capabilities

### Email System

#### SMTP Configuration
**Email Features:**
- OTP delivery for verification
- Application status notifications
- Admin notification system
- Support ticket creation
- Automated responses

**Configuration:**
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
```

### Security Features

#### Authentication Security
- Domain-restricted access (@veltech.edu.in only)
- Session timeout (30 minutes)
- CSRF protection
- Rate limiting on sensitive endpoints
- Secure cookie configuration

#### Data Protection
- Input validation and sanitization
- SQL injection prevention
- XSS protection
- File upload security
- Environment variable protection

### Site Configuration

#### Maintenance Mode
**Global System Control:**
```python
class SiteSetting(models.Model):
    maintenance_mode = models.BooleanField(default=False)
    active_approval_letter = models.BooleanField(default=True)
    active_undertaking_letter = models.BooleanField(default=True)
    active_bonafide_letter = models.BooleanField(default=True)
```

#### Announcement System
**Dynamic Content Management:**
- Dual message system
- Color-coded announcements
- Conditional display logic
- Admin-controlled visibility

## Installation & Setup

### Prerequisites
- Docker and Docker Compose
- PostgreSQL database
- Google Cloud Console account
- Cloudinary account
- Gmail SMTP access

### Environment Configuration
```bash
# Required environment variables
SECRET_KEY=your-secret-key
DEBUG=False
DATABASE_URL=postgresql://user:pass@host:port/dbname
ALLOWED_HOSTS=yourdomain.com,localhost

# Google OAuth2
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY=your-client-id
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET=your-client-secret

# Email Configuration
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
ADMIN_EMAIL=admin@veltech.edu.in

# Cloudinary
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret

# Google Sheets
GOOGLE_SHEET_ID=your-sheet-id
GOOGLE_TYPE=service_account
GOOGLE_PROJECT_ID=your-project-id
GOOGLE_PRIVATE_KEY_ID=your-private-key-id
GOOGLE_PRIVATE_KEY=your-private-key
GOOGLE_CLIENT_EMAIL=your-service-account-email
GOOGLE_CLIENT_ID=your-client-id

# Django Superuser
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_PASSWORD=secure-password
DJANGO_SUPERUSER_EMAIL=admin@veltech.edu.in
```

### Docker Deployment
```bash
# Build the container
docker build -t internship_portal .

# Run with environment variables
docker run -it -p 8000:8000 \
  -e SECRET_KEY=your-secret-key \
  -e DATABASE_URL=your-database-url \
  internship_portal
```

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic

# Start development server
python manage.py runserver
```

## Usage Guide

### For Students

#### Getting Started
1. **Login Process:**
   - Visit the portal homepage
   - Click "Accounts & Logout" in navigation
   - Use Google OAuth with VTU email (@veltech.edu.in)
   - Access dashboard upon successful authentication

2. **Applying for Internal Internships:**
   - Navigate to "Internships" in main menu
   - Browse available companies with vacancies
   - Click "Apply" on desired company
   - Fill required information (name, mobile, department)
   - Submit application (instant confirmation)

3. **External Company Applications:**
   - Click "External Application" in navigation
   - Enter VTU email for OTP verification
   - Complete comprehensive application form
   - Include industry details and referral information
   - Add additional students (up to 10 total)
   - Submit for admin review

4. **Document Upload:**
   - Access "Upload Documents" from dashboard
   - Upload required PDFs (max 2MB each):
     - Approval Letter (department approval)
     - Undertaking Letter (student commitment)
     - Bonafide Certificate (institution verification)
   - Monitor upload status on dashboard

5. **Checking Status:**
   - Use "Application Status" in navigation
   - Enter VTU number to view:
     - Internal company enrollment status
     - External application review status
     - Document submission progress
     - Attendance records

#### Dashboard Features
- **Profile Information:** Name, VTU number, email, account status
- **Application Status:** Current enrollment and application progress
- **Document Status:** Upload progress for required documents
- **Attendance Records:** Daily attendance history with company
- **Quick Actions:** Apply for internships, upload documents, logout

### For Companies

#### Attendance Management
1. **Login Process:**
   - Visit `/company/login/` endpoint
   - Enter auto-generated username and password
   - Access attendance management interface

2. **Daily Attendance:**
   - View list of assigned students
   - Select attendance date (defaults to today)
   - Mark each student as Present/Absent
   - Submit attendance for the day
   - View previous attendance records

3. **Student Information:**
   - Access student details (name, VTU number, contact)
   - View attendance history
   - Track overall attendance patterns

#### Session Management
- Sessions expire after period of inactivity
- No persistent login (security measure)
- Must re-login for each session

### For Department Staff

#### Department Dashboard
1. **Login Process:**
   - Visit `/dept/login/` endpoint
   - Use department-specific credentials
   - Access department dashboard

2. **Student Monitoring:**
   - View all department students with internships
   - Monitor document submission status
   - Track attendance percentages
   - Export student data

3. **Analytics:**
   - Department-wide statistics
   - Attendance trends
   - Document compliance rates
   - Company distribution

### For Administrators

#### System Administration
1. **Admin Panel Access:**
   - Visit `/admin/` endpoint
   - Login with superuser credentials
   - Access comprehensive management interface

2. **Company Management:**
   - Add/edit/delete companies
   - Set vacancy limits
   - Activate/deactivate companies
   - Export company data
   - View login credentials

3. **Student Management:**
   - Import students via CSV
   - Manual student creation/editing
   - Document status monitoring
   - Enrollment tracking
   - Export student data

4. **Application Review:**
   - Review external applications
   - Approve/reject with messages
   - View student group applications
   - Track application status

5. **System Configuration:**
   - Site maintenance mode control
   - Document requirement toggles
   - Announcement management
   - Downloadable files management

#### Data Import/Export
**CSV Import Process:**
1. Navigate to Student admin page
2. Click "Upload CSV" button
3. Select properly formatted CSV file
4. Review import results
5. Handle any errors or duplicates

**Export Options:**
- Student data with company assignments
- Company information with credentials
- Attendance records by date range
- Application data for analysis

## API Endpoints

### Public Endpoints
- `/` - Homepage
- `/Internships/` - Company listing
- `/check-status/` - Application status check
- `/apply/` - External application process
- `/support-login/` - Support system access

### Authenticated Endpoints
- `/dashboard/` - Student dashboard
- `/apply/<uuid>/` - Internal company application
- `/student/upload/documents/` - Document upload
- `/downloadable-files/` - File downloads

### Company Endpoints
- `/company/login/` - Company authentication
- `/company/attendance/` - Attendance management

### Department Endpoints
- `/dept/login/` - Department authentication
- `/dept/dashboard/` - Department dashboard

### Admin Endpoints
- `/admin/` - Django admin panel
- `/server-stats/` - System performance metrics

## Troubleshooting

### Common Issues

#### Authentication Problems
**Issue:** Students cannot login with VTU email
**Solution:**
- Verify Google OAuth2 configuration
- Check email domain restrictions
- Ensure proper redirect URIs in Google Console

#### Application Errors
**Issue:** Students cannot apply to companies
**Solution:**
- Check company vacancy availability
- Verify student eligibility (no existing applications)
- Review blacklist status

#### Document Upload Issues
**Issue:** PDF uploads failing
**Solution:**
- Verify file size (max 2MB)
- Ensure PDF format
- Check Cloudinary configuration
- Review file permissions

#### Attendance System Problems
**Issue:** Company cannot mark attendance
**Solution:**
- Verify company login credentials
- Check student-company assignments
- Review session timeout settings

### Error Handling

#### Custom Error Pages
- **400 Bad Request:** Invalid request format
- **403 Forbidden:** Access denied
- **404 Not Found:** Page not found
- **500 Server Error:** Internal server error

#### CSRF Protection
- Custom CSRF failure pages for different user types
- Automatic token refresh
- Secure cookie configuration

### Performance Optimization

#### Database Optimization
- Proper indexing on frequently queried fields
- Query optimization with select_related and prefetch_related
- Database connection pooling

#### Static Files Management
- Whitenoise for static file serving
- Compressed manifest storage
- CDN integration ready

#### Caching Strategy
- Session-based caching
- Database query caching
- Static file caching headers

## Security Considerations

### Data Protection
- Environment variable usage for sensitive data
- SQL injection prevention
- XSS protection
- CSRF token validation
- Secure file upload handling

### Access Control
- Role-based permissions
- Domain-restricted authentication
- Session timeout management
- Rate limiting on critical endpoints

### File Security
- PDF-only uploads
- File size limitations
- Virus scanning ready
- Secure cloud storage

## Future Enhancement Opportunities

### Scalability Improvements
- Database sharding strategies
- Microservices architecture migration
- Load balancing implementation
- Caching layer enhancement

### Feature Additions
- Real-time notifications
- Mobile application
- Advanced analytics dashboard
- Integration with university ERP systems
- Automated certificate generation

### Performance Enhancements
- Background task processing
- API optimization
- Database query optimization
- Frontend performance improvements

This comprehensive manual provides complete documentation for understanding, deploying, and maintaining the Internship Portal system. The modular architecture and comprehensive feature set make it suitable for educational institutions seeking to streamline their internship management processes.
