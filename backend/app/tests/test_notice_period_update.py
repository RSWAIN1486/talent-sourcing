import pytest
import json
from unittest.mock import patch, AsyncMock, MagicMock
from bson import ObjectId
from fastapi.testclient import TestClient
from app.main import app
from app.services.candidates import voice_screen_candidate, process_call_results
from app.tests.conftest import test_mongodb

# Mock MongoDB data for testing - using the same IDs as in the direct update script
MOCK_CANDIDATE_ID = "67bd8328b318f42cb1aa9ed2"
MOCK_JOB_ID = "67b5f915f4ab151ec65cce54"
MOCK_USER_ID = "67b5ca9f6c7cfccc20298936"
MOCK_PHONE = "+919007696846"

# Test data for specific test cases
MOCK_CANDIDATE = {
    "_id": ObjectId(MOCK_CANDIDATE_ID),
    "id": MOCK_CANDIDATE_ID,
    "job_id": ObjectId(MOCK_JOB_ID),
    "name": "Rakesh Swain",
    "email": "rswain1486@gmail.com",
    "phone": MOCK_PHONE,
    "location": "Chennai, India",
    "resume_file_id": "67bd8328b318f42cb1aa9ed0",
    "skills": {"Python": 0.9, "FastAPI": 0.8, "React": 0.75},
    "resume_score": 92.0,
    "screening_score": None,
    "screening_summary": None,
    "screening_in_progress": True,
    "created_by_id": ObjectId(MOCK_USER_ID),
    "created_at": "2025-02-25T08:45:28.382+00:00",
    "updated_at": "2025-02-28T11:07:38.378+00:00"
}

MOCK_JOB = {
    "_id": ObjectId(MOCK_JOB_ID),
    "id": MOCK_JOB_ID,
    "title": "Senior Software Engineer",
    "description": "We are looking for a senior software engineer...",
    "responsibilities": "Design and develop...",
    "requirements": "5+ years of experience...",
    "total_candidates": 1,
    "resume_screened": 1,
    "phone_screened": 0,
    "created_by_id": ObjectId(MOCK_USER_ID),
    "created_at": "2025-02-25T06:30:00.000+00:00",
    "updated_at": "2025-02-25T06:30:00.000+00:00"
}

MOCK_USER = {
    "_id": ObjectId(MOCK_USER_ID),
    "id": MOCK_USER_ID,
    "email": "admin@example.com",
    "full_name": "Admin User",
    "is_active": True,
    "is_superuser": True,
    "created_at": "2025-02-25T06:00:00.000+00:00",
    "updated_at": "2025-02-25T06:00:00.000+00:00"
}

# Mock for the Ultravox API call response
MOCK_ULTRAVOX_RESPONSE = {
    "callId": "mock-call-123",
    "joinUrl": "https://call.ultravox.ai/mock-call-123"
}

# Mock for the Twilio call response
MOCK_TWILIO_CALL = AsyncMock()
MOCK_TWILIO_CALL.sid = "mock-call-123"

# Mock response data for call completion webhook
MOCK_CALL_RESULTS = {
    "CallSid": "mock-call-123",
    "CallStatus": "completed",
    "Duration": "45",
    "To": MOCK_PHONE,
    "From": "+14155551234"
}

@pytest.fixture
def mock_database():
    """Setup mock database with test data."""
    # Mock database collections
    mock_db = MagicMock()
    mock_db.candidates = MagicMock()
    mock_db.jobs = MagicMock()
    mock_db.call_sessions = MagicMock()
    mock_db.users = MagicMock()
    
    # Configure find_one results
    mock_db.candidates.find_one = AsyncMock(return_value=MOCK_CANDIDATE)
    mock_db.jobs.find_one = AsyncMock(return_value=MOCK_JOB)
    mock_db.users.find_one = AsyncMock(return_value=MOCK_USER)
    
    # Configure update_one results
    mock_db.candidates.update_one = AsyncMock()
    mock_db.candidates.update_one.return_value.modified_count = 1
    
    mock_db.jobs.update_one = AsyncMock()
    mock_db.jobs.update_one.return_value.modified_count = 1
    
    # Mock the call_sessions collection
    mock_db.call_sessions.insert_one = AsyncMock()
    mock_db.call_sessions.insert_one.return_value.inserted_id = ObjectId()
    
    mock_db.call_sessions.find_one = AsyncMock(return_value={
        "_id": ObjectId(),
        "call_id": "mock-call-123",
        "ultravox_call_id": "mock-call-123",
        "candidate_id": ObjectId(MOCK_CANDIDATE_ID),
        "job_id": ObjectId(MOCK_JOB_ID),
        "phone_number": MOCK_PHONE,
        "status": "initiated",
        "created_by_id": ObjectId(MOCK_USER_ID),
        "created_at": "2025-02-28T12:00:00.000+00:00",
        "updated_at": "2025-02-28T12:00:00.000+00:00"
    })
    
    mock_db.call_sessions.update_one = AsyncMock()
    mock_db.call_sessions.update_one.return_value.modified_count = 1
    
    return mock_db

@pytest.mark.asyncio
async def test_notice_period_and_compensation_update(mock_database):
    """Test updating notice period and compensation via Ultravox conversation."""
    
    # Mock for the Ultravox call details API response - including notice period and compensation
    mock_call_details = {
        "callId": "mock-call-123",
        "status": "completed",
        "summary": "The candidate is available with notice period of 2 months. They are currently making $110,000 and expecting $150,000.",
        "score": 85.0,
        "notice_period": "2 months",
        "current_compensation": "$110,000",
        "expected_compensation": "$150,000"
    }
    
    # Mock messages data for transcript
    mock_messages_data = {
        "messages": [
            {
                "role": "MESSAGE_ROLE_AGENT",
                "text": "Hello, this is an AI assistant calling about the Senior Software Engineer position. What is your notice period at your current job?"
            },
            {
                "role": "MESSAGE_ROLE_USER",
                "text": "Hi, I have a notice period of 2 months."
            },
            {
                "role": "MESSAGE_ROLE_AGENT",
                "text": "Thank you. What is your current compensation package?"
            },
            {
                "role": "MESSAGE_ROLE_USER",
                "text": "I'm currently making $110,000 per year."
            },
            {
                "role": "MESSAGE_ROLE_AGENT",
                "text": "And what is your expected compensation for this new role?"
            },
            {
                "role": "MESSAGE_ROLE_USER",
                "text": "I'm looking for $150,000."
            },
            {
                "role": "MESSAGE_ROLE_AGENT",
                "text": "Thank you for that information. I'll update our records."
            }
        ]
    }
    
    # Mock the get_database function
    with patch('app.services.candidates.get_database', return_value=mock_database):
        # Mock httpx client for Ultravox API calls
        with patch('httpx.AsyncClient') as mock_httpx:
            # Configure mock responses for Ultravox API calls
            mock_client = mock_httpx.return_value.__aenter__.return_value
            
            # Mock the call details response
            mock_client.get = AsyncMock()
            mock_client.get.side_effect = [
                # First call - get call details
                MagicMock(
                    status_code=200,
                    json=AsyncMock(return_value=mock_call_details),
                    raise_for_status=AsyncMock()
                ),
                # Second call - get messages for transcript
                MagicMock(
                    status_code=200,
                    json=AsyncMock(return_value=mock_messages_data),
                    raise_for_status=AsyncMock()
                )
            ]
            
            # Call the function being tested
            result = await process_call_results(MOCK_CALL_RESULTS)
            
            # Verify the results
            assert result["status"] == "success"
            assert result["candidate_id"] == MOCK_CANDIDATE_ID
            
            # Verify database updates - candidate record should be updated
            mock_database.candidates.update_one.assert_called_once()
            
            # Verify job statistics update
            mock_database.jobs.update_one.assert_called_once()
            
            # Verify call session update
            mock_database.call_sessions.update_one.assert_called_once() 