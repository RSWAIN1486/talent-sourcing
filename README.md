# Talent Sourcing Web Application

A modern web application for talent sourcing teams to manage job postings, handle resume uploads, and conduct AI-driven resume and voice screenings for candidates.

## Demo
Check out the demo video to see the application in action.


https://github.com/user-attachments/assets/f3ff2e48-b01f-4d61-a193-192bc898cc00




## Features

### Job Management
- Create and manage detailed job postings
- Track job statistics and candidate progress
- Bulk actions for job management
- Rich text formatting for job descriptions

### Candidate Management
- Upload individual or bulk resumes (PDF/ZIP)
- AI-powered resume analysis
- Skill extraction and scoring
- Candidate profile management
- Resume download functionality
- Automated voice screening for candidates

### AI Integration
- DeepInfra API integration
- Llama model for resume analysis
- Automatic information extraction
- Skill proficiency scoring
- Overall candidate scoring
- Voice agent for phone screening with Ultravox AI

### Analytics & Reporting
- Job statistics dashboard
- Candidate screening metrics
- Resume processing statistics
- Performance analytics

## Tech Stack

### Frontend
- React 18 with TypeScript
- Material-UI v5
- React Query for state management
- React Router v6
- Axios for API communication

### Backend
- FastAPI (Python 3.11)
- MongoDB with Motor (async driver)
- GridFS for file storage
- JWT authentication
- OpenAPI/Swagger documentation

### AI Services
- DeepInfra API
- Llama model integration
- PDF text extraction
- Natural language processing
- Ultravox AI for voice synthesis
- Twilio for phone call integration

## Getting Started

### Prerequisites
- Python 3.11 or higher
- Node.js 18 or higher
- MongoDB 6.0 or higher
- Conda (recommended for environment management)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/ZeroGradAI/talent-sourcing.git
cd talent-sourcing
```

2. **Backend Setup**
```bash
# Create and activate conda environment
conda create -n talent_sourcing python=3.11
conda activate talent_sourcing

# Install backend dependencies
cd backend
pip install -e .

# Configure environment
cp .env.example .env
# Edit .env with your configuration
```

3. **Frontend Setup**
```bash
cd frontend
npm install
```

### Running the Application

Use the provided development script:
```bash
./dev.bat
```

Or run services individually:

**Backend**
```bash
cd backend
uvicorn app.main:app --reload
```

**Frontend**
```bash
cd frontend
npm run dev
```

The application will be available at:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## Project Structure

```
talent-sourcing/
├── backend/
│   ├── app/
│   │   ├── api/           # API endpoints
│   │   ├── core/          # Core configurations
│   │   ├── models/        # Data models
│   │   ├── services/      # Business logic
│   │   └── tests/         # Test files
│   ├── pyproject.toml     # Python dependencies
│   └── .env              # Environment variables
├── frontend/
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── pages/         # Page components
│   │   ├── services/      # API services
│   │   └── utils/         # Utility functions
│   └── package.json      # Node.js dependencies
├── docs/                 # Documentation
│   ├── architecture.md   # System architecture
│   ├── api-documentation.md # API reference
│   ├── deployment-guide.md # Deployment instructions
│   ├── vercel-deployment.md # Vercel deployment guide
│   └── testing-guide.md  # Testing guidelines
└── README.md
```

## Documentation

- [Architecture Overview](docs/architecture.md)
- [API Documentation](docs/api-documentation.md)
- [Deployment Guide](docs/deployment-guide.md)
- [Vercel Deployment Guide](docs/vercel-deployment.md)
- [Testing Guide](docs/testing-guide.md)

## Development

### Code Style
- Backend: Black formatter, isort for imports
- Frontend: ESLint with TypeScript rules
- Pre-commit hooks for code quality

### Testing
- Backend: pytest for unit and integration tests
- Frontend: Jest and React Testing Library
- E2E: Cypress
- Coverage requirements: 80% minimum

#### Running Backend Tests

The backend tests are organized by functionality:
- Job management tests
- Candidate management tests
- Authentication tests
- Voice screening tests
- API endpoint tests

**Running All Tests**

To run all backend tests at once:
```bash
cd backend
# Using the batch file
tests\run_tests.bat

# Or using pytest directly
python -m pytest
```

**Running Tests by Functionality**

To run tests for specific functionality:
```bash
cd backend
# Job management tests
python -m pytest tests/jobs -v

# Candidate management tests
python -m pytest tests/candidates -v

# Authentication tests
python -m pytest tests/auth -v

# Voice screening tests
python -m pytest tests/voice_screening -v

# API endpoint tests
python -m pytest tests/test_api_endpoints.py -v
```

**Test Structure**

The backend tests follow a consistent structure:
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

Each test module uses pytest fixtures defined in the corresponding `conftest.py` file to mock dependencies and set up test data.

**Test-Driven Development**

We follow Test-Driven Development (TDD) principles:
1. Write tests first
2. Run the tests (they should fail)
3. Implement the functionality
4. Run the tests again (they should pass)
5. Refactor as needed

Before implementing any new feature or fixing a bug, ensure that you have appropriate test coverage.

### Branching Strategy
- main: Production-ready code
- develop: Development branch
- feature/*: New features
- bugfix/*: Bug fixes
- release/*: Release preparation

## Deployment

See [Deployment Guide](docs/deployment-guide.md) for detailed instructions on:
- Production setup
- Environment configuration
- Server requirements
- Monitoring setup
- Backup procedures

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/)
- [React](https://reactjs.org/)
- [Material-UI](https://mui.com/)
- [MongoDB](https://www.mongodb.com/)
- [DeepInfra](https://deepinfra.com/) 
