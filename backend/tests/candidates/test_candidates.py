import pytest
import asyncio
import os
import sys
from unittest.mock import patch, AsyncMock, MagicMock
from bson import ObjectId
from datetime import datetime
from fastapi import HTTPException

# Add parent directory to path to allow imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from app.services.candidates import (
    upload_resume,
    process_pdf_file,
    get_candidates,
    get_candidate,
    get_resume_file,
    update_candidate_info,
    delete_candidate
)
from app.models.database import User

class MockUser(User):
    def __init__(self, user_dict):
        super().__init__(**user_dict)

@pytest.mark.asyncio
async def test_process_pdf_file(mock_get_database, mock_get_gridfs, mock_resume_file, mock_ai_services, mock_user):
    """Test processing a PDF file"""
    # Convert mock_user dict to User object
    user = MockUser(mock_user)
    
    # Call the process_pdf_file function
    result = await process_pdf_file(
        file_content=mock_resume_file,
        filename="test_resume.pdf",
        job_id=str(ObjectId()),
        created_by=user
    )
    
    # Verify the result
    assert result is not None
    assert "id" in result
    assert result["name"] == "Test Candidate"
    assert result["email"] == "test.candidate@example.com"
    assert result["phone"] == "+1234567890"
    assert result["location"] == "Test Location"
    assert "resume_file_id" in result
    assert result["skills"] == {"Python": 0.8, "JavaScript": 0.7}
    assert result["resume_score"] == 85.0
    
    # Verify the database was called correctly
    mock_db = mock_get_database
    mock_db.candidates.insert_one.assert_called_once()
    mock_db.jobs.update_one.assert_called_once()
    
    # Verify GridFS was called correctly
    mock_fs = mock_get_gridfs
    mock_fs.upload_from_stream.assert_called_once()

@pytest.mark.asyncio
async def test_upload_resume_pdf(mock_get_database, mock_get_gridfs, mock_upload_file, mock_ai_services, mock_user):
    """Test uploading a PDF resume"""
    # Convert mock_user dict to User object
    user = MockUser(mock_user)
    
    # Call the upload_resume function
    result = await upload_resume(
        job_id=str(ObjectId()),
        file=mock_upload_file,
        created_by=user
    )
    
    # Verify the result
    assert result is not None
    assert "id" in result
    assert result["name"] == "Test Candidate"
    assert result["email"] == "test.candidate@example.com"
    
    # Verify the database was called correctly
    mock_db = mock_get_database
    mock_db.candidates.insert_one.assert_called_once()
    mock_db.jobs.update_one.assert_called_once()

@pytest.mark.asyncio
async def test_get_candidates(mock_get_database, mock_candidate, mock_job):
    """Test getting candidates for a job"""
    job_id = str(mock_job["_id"])
    
    # Call the get_candidates function
    result = await get_candidates(job_id, skip=0, limit=10)
    
    # Verify the result
    assert result is not None
    assert len(result) == 1
    assert result[0]["id"] == str(mock_candidate["_id"])
    assert result[0]["name"] == mock_candidate["name"]
    assert result[0]["email"] == mock_candidate["email"]
    
    # Verify the database was called correctly
    mock_db = mock_get_database
    mock_db.candidates.find.assert_called_once()

@pytest.mark.asyncio
async def test_get_candidate(mock_get_database, mock_candidate, mock_job):
    """Test getting a specific candidate"""
    job_id = str(mock_job["_id"])
    candidate_id = str(mock_candidate["_id"])
    
    # Call the get_candidate function
    result = await get_candidate(job_id, candidate_id)
    
    # Verify the result
    assert result is not None
    assert result.id == candidate_id
    assert result.name == mock_candidate["name"]
    assert result.email == mock_candidate["email"]
    
    # Verify the database was called correctly
    mock_db = mock_get_database
    mock_db.candidates.find_one.assert_called_once()

@pytest.mark.asyncio
async def test_get_candidate_not_found(mock_get_database):
    """Test getting a candidate that doesn't exist"""
    # Setup the mock to return None
    mock_db = mock_get_database
    mock_db.candidates.find_one.return_value = None
    
    # Call the get_candidate function with a non-existent ID
    result = await get_candidate("507f1f77bcf86cd799439011", "507f1f77bcf86cd799439012")
    
    # Verify the result is None
    assert result is None

@pytest.mark.asyncio
async def test_get_resume_file(mock_get_database, mock_get_gridfs, mock_candidate):
    """Test getting a resume file"""
    candidate_id = str(mock_candidate["_id"])
    
    # Call the get_resume_file function
    content, filename = await get_resume_file(candidate_id)
    
    # Verify the result
    assert content is not None
    assert filename is not None
    assert content.startswith(b"%PDF-1.4")
    
    # Verify the database and GridFS were called correctly
    mock_db = mock_get_database
    mock_db.candidates.find_one.assert_called_once()
    mock_fs = mock_get_gridfs
    mock_fs.open_download_stream.assert_called_once()

@pytest.mark.asyncio
async def test_update_candidate_info(mock_get_database, mock_candidate):
    """Test updating candidate information"""
    candidate_id = str(mock_candidate["_id"])
    new_name = "Updated Test Candidate"
    new_email = "updated.test@example.com"
    
    # Setup the mock to return an updated candidate
    updated_candidate = mock_candidate.copy()
    updated_candidate["name"] = new_name
    updated_candidate["email"] = new_email
    mock_db = mock_get_database
    mock_db.candidates.find_one_and_update.return_value = updated_candidate
    
    # Call the update_candidate_info function
    result = await update_candidate_info(
        candidate_id=candidate_id,
        name=new_name,
        email=new_email
    )
    
    # Verify the result
    assert result is not None
    assert result["name"] == new_name
    assert result["email"] == new_email
    
    # Verify the database was called correctly
    mock_db.candidates.find_one_and_update.assert_called_once()

@pytest.mark.asyncio
async def test_delete_candidate(mock_get_database, mock_candidate):
    """Test deleting a candidate"""
    candidate_id = str(mock_candidate["_id"])
    
    # Setup the mock to return a successful deletion
    mock_db = mock_get_database
    mock_db.candidates.delete_one.return_value = AsyncMock(deleted_count=1)
    
    # Call the delete_candidate function
    await delete_candidate(candidate_id)
    
    # Verify the database was called correctly
    mock_db.candidates.delete_one.assert_called_once()
    mock_db.jobs.update_one.assert_called_once() 