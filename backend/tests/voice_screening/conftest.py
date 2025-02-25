import pytest
import os
import sys
import asyncio
from datetime import datetime
from bson import ObjectId
from unittest.mock import AsyncMock, MagicMock, patch
from dotenv import load_dotenv

# Add parent directory to path to allow imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

# Load environment variables from the root directory
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
dotenv_path = os.path.join(root_dir, ".env")
load_dotenv(dotenv_path)

# Fixtures for testing

@pytest.fixture
def test_phone_number():
    """Return a test phone number for voice screening tests"""
    return "+919007696846"  # This should be a valid number for testing

@pytest.fixture
def mock_twilio_client():
    """Create a mock Twilio client for testing"""
    mock_client = MagicMock()
    
    # Mock a successful call
    mock_call = MagicMock()
    mock_call.sid = "CA12345678901234567890123456789012"
    mock_call.status = "initiated"
    
    # Set up the mock calls.create method
    mock_client.calls.create.return_value = mock_call
    
    # Mock the call fetching
    mock_client.calls.return_value.fetch.return_value = mock_call
    
    return mock_client

@pytest.fixture
def mock_user():
    """Create a mock user for testing"""
    user_id = str(ObjectId())
    return {
        "_id": ObjectId(user_id),
        "id": user_id,
        "email": "test@example.com",
        "full_name": "Test User"
    }

@pytest.fixture
def mock_job():
    """Create a mock job for testing"""
    job_id = str(ObjectId())
    user_id = str(ObjectId())
    return {
        "_id": ObjectId(job_id),
        "id": job_id,
        "title": "Test Job",
        "description": "Test job description",
        "responsibilities": "Test responsibilities",
        "requirements": "Test requirements",
        "total_candidates": 0,
        "resume_screened": 0,
        "phone_screened": 0,
        "created_by_id": ObjectId(user_id),
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }

@pytest.fixture
def mock_candidate(mock_job, test_phone_number):
    """Create a mock candidate for testing"""
    candidate_id = str(ObjectId())
    return {
        "_id": ObjectId(candidate_id),
        "id": candidate_id,
        "job_id": mock_job["_id"],
        "name": "Test Candidate",
        "email": "test.candidate@example.com",
        "phone": test_phone_number,
        "location": "Test Location",
        "resume_file_id": "test_file_id",
        "skills": {"Python": 0.8, "JavaScript": 0.7},
        "resume_score": 85.0,
        "screening_score": None,
        "screening_summary": None,
        "screening_in_progress": False,
        "call_transcript": None,
        "notice_period": None,
        "current_compensation": None,
        "expected_compensation": None,
        "created_by_id": mock_job["created_by_id"],
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }

@pytest.fixture
def mock_db():
    """Create a mock database client for testing"""
    mock_database = AsyncMock()
    
    # Mock collections
    mock_database.users = AsyncMock()
    mock_database.jobs = AsyncMock()
    mock_database.candidates = AsyncMock()
    mock_database.call_sessions = AsyncMock()
    
    # Setup default return values
    mock_database.candidates.find_one.return_value = None
    mock_database.jobs.find_one.return_value = None
    mock_database.users.find_one.return_value = None
    
    return mock_database

# Helper to patch database and Twilio client
@pytest.fixture
def patch_dependencies(mock_db, mock_twilio_client):
    """Patch database and Twilio client for tests"""
    with patch("app.services.voice_screening.Client", return_value=mock_twilio_client), \
         patch("motor.motor_asyncio.AsyncIOMotorClient", return_value=mock_db):
        yield 