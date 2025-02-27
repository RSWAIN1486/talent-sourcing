import pytest
import os
import sys
import asyncio
from datetime import datetime, UTC
from bson import ObjectId
from unittest.mock import AsyncMock, MagicMock, patch
from dotenv import load_dotenv
from fastapi import UploadFile
from io import BytesIO
from tempfile import SpooledTemporaryFile

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
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC)
    }

@pytest.fixture
def mock_job():
    """Create a mock job for testing"""
    job_id = str(ObjectId())
    user_id = str(ObjectId())
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
        "created_by_id": ObjectId(user_id),
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC)
    }

@pytest.fixture
def mock_candidate(mock_job):
    """Create a mock candidate for testing"""
    candidate_id = str(ObjectId())
    file_id = str(ObjectId())
    return {
        "_id": ObjectId(candidate_id),
        "id": candidate_id,
        "job_id": mock_job["_id"],
        "name": "Test Candidate",
        "email": "test.candidate@example.com",
        "phone": "+1234567890",
        "location": "Test Location",
        "resume_file_id": file_id,
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
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC)
    }

@pytest.fixture
def mock_resume_file():
    """Create a mock PDF file for testing"""
    # Simple PDF content for testing
    pdf_content = b"%PDF-1.4\n1 0 obj\n<</Type/Catalog/Pages 2 0 R>>\nendobj\n2 0 obj\n<</Type/Pages/Kids[3 0 R]/Count 1>>\nendobj\n3 0 obj\n<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R/Resources<<>>>>\nendobj\nxref\n0 4\n0000000000 65535 f\n0000000010 00000 n\n0000000053 00000 n\n0000000102 00000 n\ntrailer\n<</Size 4/Root 1 0 R>>\nstartxref\n178\n%%EOF"
    return pdf_content

@pytest.fixture
def mock_upload_file(mock_resume_file):
    """Create a mock UploadFile for testing"""
    # Create a SpooledTemporaryFile with the mock PDF content
    spooled_file = SpooledTemporaryFile()
    spooled_file.write(mock_resume_file)
    spooled_file.seek(0)
    
    # Create the UploadFile instance
    file = UploadFile(
        file=spooled_file,
        filename="test_resume.pdf",
        size=len(mock_resume_file),
        headers={"content-type": "application/pdf"}
    )
    return file

@pytest.fixture
def mock_gridfs():
    """Create a mock GridFS for testing"""
    mock_fs = AsyncMock()
    file_id = ObjectId()
    mock_fs.upload_from_stream.return_value = file_id
    
    # Mock file retrieval
    mock_fs.open_download_stream.return_value = AsyncMock(
        read=AsyncMock(return_value=b"%PDF-1.4\nTest PDF content")
    )
    
    return mock_fs

class MockCursor:
    def __init__(self, data):
        self.data = data
        self._skip = 0
        self._limit = None

    def skip(self, count):
        self._skip = count
        return self

    def limit(self, count):
        self._limit = count
        return self

    async def to_list(self, length=None):
        if length is not None:
            self._limit = length
        end = None if self._limit is None else self._skip + self._limit
        return self.data[self._skip:end]

@pytest.fixture
def mock_db(mock_job, mock_candidate):
    """Create a mock database client for testing"""
    mock_database = AsyncMock()
    
    # Mock collections
    mock_database.users = AsyncMock()
    mock_database.jobs = AsyncMock()
    mock_database.candidates = AsyncMock()
    
    # Setup default return values
    mock_database.jobs.find_one.return_value = mock_job
    mock_database.candidates.find_one.return_value = mock_candidate
    mock_database.candidates.insert_one.return_value = AsyncMock(inserted_id=mock_candidate["_id"])
    
    # Create a mock cursor with our data
    mock_cursor = MockCursor([mock_candidate])
    
    # Make find() return the cursor
    mock_database.candidates.find = lambda *args, **kwargs: mock_cursor
    
    # Mock count_documents
    mock_database.candidates.count_documents.return_value = 1
    
    return mock_database

@pytest.fixture
def mock_get_database(mock_db):
    """Patch the get_database function to return our mock"""
    async def _get_database():
        return mock_db
    
    with patch("app.services.candidates.get_database", _get_database):
        yield mock_db

@pytest.fixture
def mock_get_gridfs(mock_gridfs):
    """Patch the get_gridfs function to return our mock"""
    async def _get_gridfs():
        return mock_gridfs
    
    with patch("app.services.candidates.get_gridfs", _get_gridfs):
        yield mock_gridfs

@pytest.fixture
def mock_ai_services():
    """Mock the AI services for resume processing"""
    with patch("app.services.candidates.extract_resume_info", 
               return_value={"name": "Test Candidate", "email": "test.candidate@example.com", "phone": "+1234567890", "location": "Test Location"}), \
         patch("app.services.candidates.analyze_resume", 
               return_value={"skills": {"Python": 0.8, "JavaScript": 0.7}, "score": 85.0}):
        yield 