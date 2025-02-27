import pytest
import os
import sys
import asyncio
from unittest.mock import patch, AsyncMock, MagicMock
from fastapi import FastAPI
from fastapi.testclient import TestClient
from bson import ObjectId
from datetime import datetime

# Add parent directory to path to allow imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Import app modules
from app.main import app
from app.api.v1.api import api_router
from app.services.auth import get_current_active_user

# Create a test client
client = TestClient(app)

# Mock user for authentication
mock_user = {
    "_id": ObjectId(),
    "id": str(ObjectId()),
    "email": "test@example.com",
    "full_name": "Test User",
    "is_active": True,
    "is_superuser": False
}

# Override the dependency for authentication
@pytest.fixture(autouse=True)
def override_dependency():
    """Override the dependency for authentication"""
    async def mock_get_current_active_user():
        return mock_user
    
    app.dependency_overrides[get_current_active_user] = mock_get_current_active_user
    yield
    app.dependency_overrides = {}

# Test cases for API endpoints

def test_create_job():
    """Test creating a job through the API"""
    # Mock the create_job service
    with patch("app.api.v1.jobs.jobs.create_job") as mock_create_job:
        # Setup the mock
        mock_create_job.return_value = {
            "id": str(ObjectId()),
            "title": "Test Job",
            "description": "Test Description",
            "responsibilities": "Test Responsibilities",
            "requirements": "Test Requirements",
            "total_candidates": 0,
            "resume_screened": 0,
            "phone_screened": 0,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        # Make the request
        response = client.post(
            "/api/v1/jobs/",
            json={
                "title": "Test Job",
                "description": "Test Description",
                "responsibilities": "Test Responsibilities",
                "requirements": "Test Requirements"
            }
        )
        
        # Verify the response
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Test Job"
        assert data["description"] == "Test Description"
        assert data["responsibilities"] == "Test Responsibilities"
        assert data["requirements"] == "Test Requirements"
        
        # Verify the service was called
        mock_create_job.assert_called_once()

def test_get_jobs():
    """Test getting jobs through the API"""
    # Mock the get_jobs service
    with patch("app.api.v1.jobs.jobs.get_jobs") as mock_get_jobs:
        # Setup the mock
        mock_get_jobs.return_value = [
            {
                "id": str(ObjectId()),
                "title": "Test Job 1",
                "description": "Test Description 1",
                "responsibilities": "Test Responsibilities 1",
                "requirements": "Test Requirements 1",
                "total_candidates": 0,
                "resume_screened": 0,
                "phone_screened": 0,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            },
            {
                "id": str(ObjectId()),
                "title": "Test Job 2",
                "description": "Test Description 2",
                "responsibilities": "Test Responsibilities 2",
                "requirements": "Test Requirements 2",
                "total_candidates": 0,
                "resume_screened": 0,
                "phone_screened": 0,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
        ]
        
        # Make the request
        response = client.get("/api/v1/jobs/")
        
        # Verify the response
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["title"] == "Test Job 1"
        assert data[1]["title"] == "Test Job 2"
        
        # Verify the service was called
        mock_get_jobs.assert_called_once()

def test_get_job():
    """Test getting a specific job through the API"""
    job_id = str(ObjectId())
    
    # Mock the get_job service
    with patch("app.api.v1.jobs.jobs.get_job") as mock_get_job:
        # Setup the mock
        mock_get_job.return_value = {
            "_id": ObjectId(job_id),
            "title": "Test Job",
            "description": "Test Description",
            "responsibilities": "Test Responsibilities",
            "requirements": "Test Requirements",
            "total_candidates": 0,
            "resume_screened": 0,
            "phone_screened": 0,
            "created_by_id": ObjectId(),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # Make the request
        response = client.get(f"/api/v1/jobs/{job_id}")
        
        # Verify the response
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == job_id
        assert data["title"] == "Test Job"
        
        # Verify the service was called
        mock_get_job.assert_called_once_with(job_id)

def test_get_job_stats():
    """Test getting job statistics through the API"""
    # Mock the get_job_stats service
    with patch("app.api.v1.jobs.get_job_stats") as mock_get_job_stats:
        # Setup the mock
        mock_get_job_stats.return_value = {
            "total_jobs": 10,
            "total_candidates": 50,
            "resume_screened": 40,
            "phone_screened": 30
        }
        
        # Make the request
        response = client.get("/api/v1/jobs/stats")
        
        # Verify the response
        assert response.status_code == 200
        data = response.json()
        assert data["total_jobs"] == 10
        assert data["total_candidates"] == 50
        assert data["resume_screened"] == 40
        assert data["phone_screened"] == 30
        
        # Verify the service was called
        mock_get_job_stats.assert_called_once()

def test_upload_resume():
    """Test uploading a resume through the API"""
    job_id = str(ObjectId())
    candidate_id = str(ObjectId())
    
    # Mock the upload_resume service
    with patch("app.api.v1.candidates.upload_resume") as mock_upload_resume:
        # Setup the mock
        mock_upload_resume.return_value = {
            "id": candidate_id,
            "job_id": job_id,
            "name": "Test Candidate",
            "email": "test.candidate@example.com",
            "phone": "+1234567890",
            "location": "Test Location",
            "resume_file_id": str(ObjectId()),
            "skills": {"Python": 0.8, "JavaScript": 0.7},
            "resume_score": 85.0,
            "screening_score": None,
            "screening_summary": None,
            "screening_in_progress": False,
            "call_transcript": None,
            "notice_period": None,
            "current_compensation": None,
            "expected_compensation": None,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        # Create a test file
        test_file_content = b"%PDF-1.4\nTest PDF content"
        
        # Make the request
        response = client.post(
            f"/api/v1/{job_id}/upload",
            files={"file": ("test_resume.pdf", test_file_content, "application/pdf")}
        )
        
        # Verify the response
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == candidate_id
        assert data["job_id"] == job_id
        assert data["name"] == "Test Candidate"
        assert data["email"] == "test.candidate@example.com"
        
        # Verify the service was called
        mock_upload_resume.assert_called_once()

def test_get_candidates():
    """Test getting candidates through the API"""
    job_id = str(ObjectId())
    
    # Mock the get_candidates service
    with patch("app.api.v1.candidates.get_candidates") as mock_get_candidates:
        # Setup the mock
        mock_get_candidates.return_value = [
            {
                "id": str(ObjectId()),
                "job_id": job_id,
                "name": "Test Candidate 1",
                "email": "test1@example.com",
                "phone": "+1234567890",
                "location": "Test Location 1",
                "resume_file_id": str(ObjectId()),
                "skills": {"Python": 0.8, "JavaScript": 0.7},
                "resume_score": 85.0,
                "screening_score": None,
                "screening_summary": None,
                "screening_in_progress": False,
                "call_transcript": None,
                "notice_period": None,
                "current_compensation": None,
                "expected_compensation": None
            },
            {
                "id": str(ObjectId()),
                "job_id": job_id,
                "name": "Test Candidate 2",
                "email": "test2@example.com",
                "phone": "+1987654321",
                "location": "Test Location 2",
                "resume_file_id": str(ObjectId()),
                "skills": {"Python": 0.9, "React": 0.8},
                "resume_score": 90.0,
                "screening_score": None,
                "screening_summary": None,
                "screening_in_progress": False,
                "call_transcript": None,
                "notice_period": None,
                "current_compensation": None,
                "expected_compensation": None
            }
        ]
        
        # Make the request
        response = client.get(f"/api/v1/{job_id}/candidates")
        
        # Verify the response
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["name"] == "Test Candidate 1"
        assert data[1]["name"] == "Test Candidate 2"
        
        # Verify the service was called
        mock_get_candidates.assert_called_once_with(job_id, 0, 10) 