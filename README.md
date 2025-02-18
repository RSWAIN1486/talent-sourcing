# Talent Sourcing Web Application

A modern web application for talent sourcing teams to manage job postings, handle resume uploads, and conduct AI-driven resume and voice screenings for candidates.

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

### AI Integration
- DeepInfra API integration
- Llama model for resume analysis
- Automatic information extraction
- Skill proficiency scoring
- Overall candidate scoring

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
│   └── testing-guide.md  # Testing guidelines
└── README.md
```

## Documentation

- [Architecture Overview](docs/architecture.md)
- [API Documentation](docs/api-documentation.md)
- [Deployment Guide](docs/deployment-guide.md)
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