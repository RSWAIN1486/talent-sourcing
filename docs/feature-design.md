# Feature Design: Talent Sourcing Web Application

## Overview
The Talent Sourcing Web Application is a modern platform designed to streamline the recruitment process by combining traditional job posting management with AI-powered candidate screening capabilities.

## Core Features

### 1. Job Management
- **Job Posting Creation**
  - Create detailed job postings with title, description, responsibilities, and requirements
  - Rich text formatting for job descriptions
  - Automatic tracking of job statistics (total candidates, screened candidates)

- **Job Listing and Search**
  - Grid view of all job postings
  - Quick stats display for each job (candidates, screening status)
  - Bulk actions (delete multiple jobs)
  - Sync candidate counts with actual database numbers

### 2. Candidate Management
- **Resume Processing**
  - Upload individual PDF resumes or bulk upload via ZIP files
  - Automatic text extraction from PDF files
  - GridFS storage for efficient file management
  - Resume download functionality

- **AI-Powered Analysis**
  - Integration with DeepInfra's Llama model for resume analysis
  - Automatic extraction of:
    - Candidate information (name, email, phone, location)
    - Technical skills with proficiency ratings (0-1 scale)
    - Overall candidate score based on job requirements
  - Structured storage of analysis results

- **Candidate Tracking**
  - Detailed candidate profiles with extracted information
  - Skills visualization with proficiency levels
  - Resume and screening scores tracking
  - Phone screening integration (planned)

### 3. Authentication & Authorization
- **User Management**
  - JWT-based authentication
  - Role-based access control (regular users vs superusers)
  - Secure password hashing using bcrypt
  - Token-based session management

### 4. Analytics & Reporting
- **Dashboard Statistics**
  - Total jobs count
  - Total candidates processed
  - Resume screening statistics
  - Phone screening statistics

## Technical Implementation

### Frontend
- **Framework**: React with TypeScript
- **UI Components**: Material-UI (MUI)
- **State Management**: React Query for server state
- **Form Handling**: React Hook Form with Yup validation
- **Routing**: React Router v6
- **API Communication**: Axios with interceptors

### Backend
- **Framework**: FastAPI
- **Database**: MongoDB with Motor (async driver)
- **File Storage**: GridFS for resume storage
- **Authentication**: JWT with OAuth2
- **AI Integration**: DeepInfra API for Llama model
- **API Documentation**: OpenAPI/Swagger

## User Experience
- Dark/Light theme support
- Responsive design for all screen sizes
- Intuitive job and candidate management
- Real-time feedback for user actions
- Progress indicators for long-running operations
- Error handling with user-friendly messages

## Security Features
- Password hashing with bcrypt
- JWT token-based authentication
- CORS protection
- Environment-based configuration
- Secure file upload handling
- Input validation and sanitization

## Future Enhancements
1. Voice screening integration
2. Advanced analytics dashboard
3. Email notifications
4. Candidate communication system
5. Interview scheduling
6. Custom AI model training
7. Enhanced reporting capabilities 