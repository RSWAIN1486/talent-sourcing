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
cd backend
tests\run_tests.bat

# Or using pytest directly
python -m pytest

# Run specific test modules
python -m pytest tests/jobs -v
python -m pytest tests/candidates -v
python -m pytest tests/auth -v
python -m pytest tests/voice_screening -v
python -m pytest tests/test_api_endpoints.py -v

# Run with coverage
pytest --cov=app

# Generate coverage report
pytest --cov=app --cov-report=html
```

### Test Structure

The backend tests are organized by functionality:

```
backend/tests/
├── jobs/                  # Job management tests
│   ├── conftest.py        # Job test fixtures
│   └── test_jobs.py       # Job service tests
├── candidates/            # Candidate management tests
│   ├── conftest.py        # Candidate test fixtures
│   └── test_candidates.py # Candidate service tests
├── auth/                  # Authentication tests
│   ├── conftest.py        # Auth test fixtures
│   └── test_auth.py       # Auth service tests
├── voice_screening/       # Voice screening tests
│   ├── conftest.py        # Voice screening test fixtures
│   └── test_voice_screening.py # Voice screening service tests
├── test_api_endpoints.py  # API endpoint integration tests
└── run_tests.bat          # Batch file to run all tests
```

### Test Fixtures

Each test module uses pytest fixtures defined in the corresponding `conftest.py` file to mock dependencies and set up test data. For example:

```python
# Example from jobs/conftest.py
@pytest.fixture
def mock_job():
    """Create a mock job for testing"""
    job_id = str(ObjectId())
    return {
        "_id": ObjectId(job_id),
        "id": job_id,
        "title": "Test Software Engineer",
        "description": "This is a test job description",
        "responsibilities": "Test responsibilities",
        "requirements": "Test requirements",
        "total_candidates": 0,
        "resume_screened": 0,
        "phone_screened": 0,
        "created_by_id": ObjectId(),
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }

@pytest.fixture
def mock_db(mock_job):
    """Create a mock database client for testing"""
    mock_database = AsyncMock()
    
    # Mock collections
    mock_database.users = AsyncMock()
    mock_database.jobs = AsyncMock()
    mock_database.candidates = AsyncMock()
    
    # Setup default return values
    mock_database.jobs.find_one.return_value = mock_job
    
    return mock_database
```

### Test-Driven Development

We follow Test-Driven Development (TDD) principles:

1. **Write tests first**: Before implementing a feature, write tests that define the expected behavior.
2. **Run the tests**: Initially, they should fail since the functionality doesn't exist yet.
3. **Implement the functionality**: Write the minimum code needed to make the tests pass.
4. **Run the tests again**: Verify that the implementation works correctly.
5. **Refactor**: Clean up the code while ensuring tests continue to pass.

### Testing Specific Functionalities

#### Job Management Tests

Tests for job creation, retrieval, updating, and deletion:

```python
@pytest.mark.asyncio
async def test_create_job(mock_get_database, mock_job_data, mock_user):
    """Test creating a new job"""
    result = await create_job(
        title=mock_job_data["title"],
        description=mock_job_data["description"],
        responsibilities=mock_job_data["responsibilities"],
        requirements=mock_job_data["requirements"],
        created_by=mock_user
    )
    
    assert result is not None
    assert "id" in result
    assert result["title"] == mock_job_data["title"]
```

#### Candidate Management Tests

Tests for resume upload, candidate creation, and retrieval:

```python
@pytest.mark.asyncio
async def test_process_pdf_file(mock_get_database, mock_get_gridfs, mock_resume_file, mock_ai_services, mock_user):
    """Test processing a PDF file"""
    user = MockUser(mock_user)
    
    result = await process_pdf_file(
        file_content=mock_resume_file,
        filename="test_resume.pdf",
        job_id=str(ObjectId()),
        created_by=user
    )
    
    assert result is not None
    assert "id" in result
    assert result["name"] == "Test Candidate"
```

#### Authentication Tests

Tests for user authentication, token generation, and validation:

```python
@pytest.mark.asyncio
async def test_authenticate_user_success(mock_get_database, mock_user, mock_password_context):
    """Test successful user authentication"""
    email = mock_user["email"]
    password = "testpassword123"
    
    result = await authenticate_user(email, password)
    
    assert result is not None
    assert result["email"] == email
```

#### Voice Screening Tests

Tests for voice screening functionality:

```python
@pytest.mark.asyncio
async def test_initiate_screening_call(mock_db, mock_twilio_client, mock_candidate):
    """Test initiating a voice screening call"""
    result = await initiate_screening_call(
        candidate_id=str(mock_candidate["_id"]),
        user=mock_user
    )
    
    assert result is not None
    assert "call_id" in result
```

#### API Endpoint Tests

Tests for API endpoints using FastAPI's TestClient:

```python
def test_create_job():
    """Test creating a job through the API"""
    with patch("app.api.v1.jobs.jobs.create_job") as mock_create_job:
        mock_create_job.return_value = {
            "id": str(ObjectId()),
            "title": "Test Job",
            "description": "Test Description"
        }
        
        response = client.post(
            "/api/v1/jobs/",
            json={
                "title": "Test Job",
                "description": "Test Description"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Test Job"
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