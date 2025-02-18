# Testing Guide

## Overview
This guide covers testing strategies and procedures for both frontend and backend components of the Talent Sourcing Web Application.

## Backend Testing

### Unit Tests

1. **Authentication Tests**
```python
def test_create_access_token():
    """Test JWT token generation"""
    
def test_verify_password():
    """Test password verification"""
    
def test_get_password_hash():
    """Test password hashing"""
```

2. **Job Management Tests**
```python
def test_create_job():
    """Test job creation"""
    
def test_get_job():
    """Test job retrieval"""
    
def test_update_job():
    """Test job update"""
    
def test_delete_job():
    """Test job deletion"""
```

3. **Candidate Management Tests**
```python
def test_create_candidate():
    """Test candidate creation"""
    
def test_process_resume():
    """Test resume processing"""
    
def test_analyze_resume():
    """Test AI analysis"""
```

### Integration Tests

1. **API Endpoint Tests**
```python
def test_job_endpoints():
    """Test job API endpoints"""
    
def test_candidate_endpoints():
    """Test candidate API endpoints"""
    
def test_auth_endpoints():
    """Test authentication endpoints"""
```

2. **Database Tests**
```python
def test_mongodb_operations():
    """Test MongoDB CRUD operations"""
    
def test_gridfs_operations():
    """Test GridFS file operations"""
```

### Running Tests
```bash
# Run all tests
pytest

# Run specific test file
pytest test_jobs.py

# Run with coverage
pytest --cov=app

# Generate coverage report
pytest --cov=app --cov-report=html
```

## Frontend Testing

### Unit Tests

1. **Component Tests**
```typescript
describe('JobCard', () => {
    it('renders job details correctly', () => {
        // Test implementation
    });
    
    it('handles click events', () => {
        // Test implementation
    });
});

describe('CandidateList', () => {
    it('renders candidates correctly', () => {
        // Test implementation
    });
    
    it('handles pagination', () => {
        // Test implementation
    });
});
```

2. **Hook Tests**
```typescript
describe('useAuth', () => {
    it('handles login correctly', () => {
        // Test implementation
    });
    
    it('maintains authentication state', () => {
        // Test implementation
    });
});
```

3. **Utility Tests**
```typescript
describe('formatters', () => {
    it('formats dates correctly', () => {
        // Test implementation
    });
    
    it('formats numbers correctly', () => {
        // Test implementation
    });
});
```

### Integration Tests

1. **Page Tests**
```typescript
describe('JobDetails Page', () => {
    it('loads job data correctly', () => {
        // Test implementation
    });
    
    it('handles candidate uploads', () => {
        // Test implementation
    });
});
```

2. **API Integration Tests**
```typescript
describe('API Client', () => {
    it('handles authentication correctly', () => {
        // Test implementation
    });
    
    it('handles API errors correctly', () => {
        // Test implementation
    });
});
```

### Running Tests
```bash
# Run all tests
npm test

# Run with coverage
npm test -- --coverage

# Run in watch mode
npm test -- --watch
```

## E2E Testing

### Cypress Tests

1. **Setup Cypress**
```bash
npm install cypress --save-dev
```

2. **Write Test Scenarios**
```javascript
describe('Job Management', () => {
    beforeEach(() => {
        cy.login();
    });
    
    it('creates a new job', () => {
        cy.visit('/jobs');
        cy.get('[data-testid="create-job-button"]').click();
        // Fill form and submit
    });
    
    it('uploads a resume', () => {
        cy.visit('/jobs/1');
        cy.get('[data-testid="upload-resume"]').attachFile('test.pdf');
        // Verify upload
    });
});
```

3. **Run Tests**
```bash
# Open Cypress
npm run cypress:open

# Run in headless mode
npm run cypress:run
```

## Performance Testing

### Backend Performance

1. **Load Testing with Locust**
```python
from locust import HttpUser, task, between

class JobsUser(HttpUser):
    wait_time = between(1, 3)
    
    @task
    def get_jobs(self):
        self.client.get("/api/v1/jobs")
    
    @task
    def create_job(self):
        self.client.post("/api/v1/jobs", json={...})
```

2. **Run Load Tests**
```bash
locust -f locustfile.py --host=http://localhost:8000
```

### Frontend Performance

1. **Lighthouse Tests**
```bash
# Install Lighthouse
npm install -g lighthouse

# Run tests
lighthouse http://localhost:3000 --view
```

## Test Coverage Requirements

### Backend Coverage
- Minimum 80% code coverage
- All API endpoints tested
- All database operations tested
- All business logic tested

### Frontend Coverage
- All components tested
- All pages tested
- All user interactions tested
- All API integrations tested

## Continuous Integration

### GitHub Actions Workflow
```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -e .[dev]
    
    - name: Run tests
      run: |
        pytest --cov=app
    
    - name: Upload coverage
      uses: codecov/codecov-action@v1
```

## Test Data Management

### Test Database
```python
@pytest.fixture
def test_db():
    """Create test database"""
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.MONGODB_DB_NAME + "_test"]
    yield db
    client.drop_database(db.name)
```

### Mock Data
```python
@pytest.fixture
def mock_job():
    """Create mock job data"""
    return {
        "title": "Test Job",
        "description": "Test Description",
        "requirements": "Test Requirements",
        "responsibilities": "Test Responsibilities"
    }
``` 