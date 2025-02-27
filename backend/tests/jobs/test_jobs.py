import pytest
import asyncio
import os
import sys
from unittest.mock import patch, AsyncMock, MagicMock
from bson import ObjectId
from datetime import datetime

# Add parent directory to path to allow imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from app.services.jobs import (
    create_job,
    get_job,
    get_jobs,
    update_job,
    delete_job,
    get_job_stats,
    sync_job_candidates_count
)

@pytest.mark.asyncio
async def test_create_job(mock_get_database, mock_job_data, mock_user):
    """Test creating a new job"""
    # Call the create_job function
    result = await create_job(
        title=mock_job_data["title"],
        description=mock_job_data["description"],
        responsibilities=mock_job_data["responsibilities"],
        requirements=mock_job_data["requirements"],
        created_by=mock_user
    )
    
    # Verify the result
    assert result is not None
    assert "id" in result
    assert result["title"] == mock_job_data["title"]
    assert result["description"] == mock_job_data["description"]
    assert result["responsibilities"] == mock_job_data["responsibilities"]
    assert result["requirements"] == mock_job_data["requirements"]
    assert result["total_candidates"] == 0
    assert result["resume_screened"] == 0
    assert result["phone_screened"] == 0
    
    # Verify the database was called correctly
    mock_db = mock_get_database
    mock_db.jobs.insert_one.assert_called_once()

@pytest.mark.asyncio
async def test_get_job(mock_get_database, mock_job):
    """Test getting a job by ID"""
    job_id = str(mock_job["_id"])
    
    # Call the get_job function
    result = await get_job(job_id)
    
    # Verify the result
    assert result is not None
    assert result["_id"] == mock_job["_id"]
    
    # Verify the database was called correctly
    mock_db = mock_get_database
    mock_db.jobs.find_one.assert_called_once()

@pytest.mark.asyncio
async def test_get_job_not_found(mock_get_database):
    """Test getting a job that doesn't exist"""
    # Setup the mock to return None
    mock_db = mock_get_database
    mock_db.jobs.find_one.return_value = None
    
    # Call the get_job function with a non-existent ID
    result = await get_job("507f1f77bcf86cd799439011")
    
    # Verify the result is None
    assert result is None

@pytest.mark.asyncio
async def test_get_jobs(mock_get_database, mock_job):
    """Test getting a list of jobs"""
    # Call the get_jobs function
    result = await get_jobs(skip=0, limit=10)
    
    # Verify the result
    assert result is not None
    assert len(result) == 1
    assert result[0]["id"] == str(mock_job["_id"])
    
    # Verify the database was called correctly
    mock_db = mock_get_database
    mock_db.jobs.find.assert_called_once()

@pytest.mark.asyncio
async def test_update_job(mock_get_database, mock_job):
    """Test updating a job"""
    job_id = str(mock_job["_id"])
    updated_title = "Updated Test Job"
    
    # Setup the mock to return an updated job
    updated_job = mock_job.copy()
    updated_job["title"] = updated_title
    mock_db = mock_get_database
    mock_db.jobs.find_one_and_update.return_value = updated_job
    
    # Call the update_job function
    result = await update_job(
        job_id=job_id,
        title=updated_title
    )
    
    # Verify the result
    assert result is not None
    assert result["title"] == updated_title
    
    # Verify the database was called correctly
    mock_db.jobs.find_one_and_update.assert_called_once()

@pytest.mark.asyncio
async def test_delete_job(mock_get_database):
    """Test deleting a job"""
    job_id = "507f1f77bcf86cd799439011"
    
    # Setup the mock to return a successful deletion
    mock_db = mock_get_database
    mock_db.jobs.delete_one.return_value = AsyncMock(deleted_count=1)
    
    # Call the delete_job function
    result = await delete_job(job_id)
    
    # Verify the result
    assert result is True
    
    # Verify the database was called correctly
    mock_db.jobs.delete_one.assert_called_once()

@pytest.mark.asyncio
async def test_get_job_stats(mock_get_database):
    """Test getting job statistics"""
    # Call the get_job_stats function
    result = await get_job_stats()
    
    # Verify the result
    assert result is not None
    assert "total_jobs" in result
    assert "total_candidates" in result
    assert "resume_screened" in result
    assert "phone_screened" in result
    
    # Verify the database was called correctly
    mock_db = mock_get_database
    mock_db.jobs.aggregate.assert_called_once()

@pytest.mark.asyncio
async def test_sync_job_candidates_count(mock_get_database, mock_job):
    """Test syncing job candidates count"""
    job_id = str(mock_job["_id"])
    
    # Setup the mocks for candidate counts
    mock_db = mock_get_database
    mock_db.candidates.count_documents.side_effect = [10, 8, 5]  # total, resume, phone
    mock_db.jobs.find_one_and_update.return_value = {
        **mock_job,
        "total_candidates": 10,
        "resume_screened": 8,
        "phone_screened": 5
    }
    
    # Call the sync_job_candidates_count function
    result = await sync_job_candidates_count(job_id)
    
    # Verify the result
    assert result is not None
    assert result["total_candidates"] == 10
    assert result["resume_screened"] == 8
    assert result["phone_screened"] == 5
    
    # Verify the database was called correctly
    assert mock_db.candidates.count_documents.call_count == 3
    mock_db.jobs.find_one_and_update.assert_called_once() 