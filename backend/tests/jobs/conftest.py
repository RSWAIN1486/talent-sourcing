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
def mock_user():
    """Create a mock user for testing"""
    user_id = str(ObjectId())
    return {
        "_id": ObjectId(user_id),
        "id": user_id,
        "email": "test@example.com",
        "full_name": "Test User",
        "is_active": True,
        "is_superuser": False,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }

@pytest.fixture
def mock_job_data():
    """Create mock job data for testing"""
    return {
        "title": "Test Software Engineer",
        "description": "This is a test job description",
        "responsibilities": "Test responsibilities",
        "requirements": "Test requirements"
    }

@pytest.fixture
def mock_job(mock_user):
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
        "created_by_id": mock_user["_id"],
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }

@pytest.fixture
def mock_db(mock_job):
    """Create a mock database client for testing"""
    mock_database = MagicMock()
    
    # Mock collections
    mock_database.users = MagicMock()
    mock_database.jobs = MagicMock()
    mock_database.candidates = MagicMock()
    
    # Setup default return values
    mock_database.jobs.find_one = AsyncMock(return_value=mock_job)
    mock_database.jobs.insert_one = AsyncMock(return_value=MagicMock(inserted_id=mock_job["_id"]))
    mock_database.jobs.find_one_and_update = AsyncMock(return_value=mock_job)
    mock_database.jobs.delete_one = AsyncMock(return_value=MagicMock(deleted_count=1))
    mock_database.jobs.update_one = AsyncMock()
    
    # Mock find with cursor that supports method chaining
    mock_cursor = MagicMock()
    mock_cursor.to_list = AsyncMock(return_value=[mock_job])
    mock_cursor.sort.return_value = mock_cursor
    mock_cursor.skip.return_value = mock_cursor
    mock_cursor.limit.return_value = mock_cursor
    mock_database.jobs.find.return_value = mock_cursor
    
    # Mock aggregate with cursor
    mock_agg_cursor = MagicMock()
    mock_agg_cursor.to_list = AsyncMock(return_value=[{
        "_id": None,
        "total_jobs": 10,
        "total_candidates": 50,
        "resume_screened": 40,
        "phone_screened": 30
    }])
    mock_database.jobs.aggregate.return_value = mock_agg_cursor
    
    # Mock count_documents
    mock_database.jobs.count_documents = AsyncMock(return_value=1)
    mock_database.candidates.count_documents = AsyncMock(return_value=5)
    
    return mock_database

@pytest.fixture
def mock_get_database(mock_db):
    """Patch the get_database function to return our mock"""
    # Create an async function that returns the mock_db
    async def _get_database():
        return mock_db
    
    with patch("app.services.jobs.get_database", _get_database):
        yield mock_db 