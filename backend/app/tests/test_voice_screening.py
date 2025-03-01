import pytest
import json
from unittest.mock import patch, AsyncMock
from bson import ObjectId
from fastapi.testclient import TestClient
from app.main import app
from app.services.candidates import voice_screen_candidate, process_call_results
from app.core.mongodb import get_database

# Mock MongoDB data for testing
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
async def mock_database():
    """Setup mock database with test data."""
    # Mock database collections
    mock_db = AsyncMock()
    mock_db.candidates = AsyncMock()
    mock_db.jobs = AsyncMock()
    mock_db.call_sessions = AsyncMock()
    mock_db.users = AsyncMock()
    
    # Configure find_one results
    mock_db.candidates.find_one.return_value = MOCK_CANDIDATE
    mock_db.jobs.find_one.return_value = MOCK_JOB
    mock_db.users.find_one.return_value = MOCK_USER
    
    # Configure update_one results
    mock_db.candidates.update_one.return_value = AsyncMock()
    mock_db.candidates.update_one.return_value.modified_count = 1
    
    mock_db.jobs.update_one.return_value = AsyncMock()
    mock_db.jobs.update_one.return_value.modified_count = 1
    
    # Mock the call_sessions collection
    mock_db.call_sessions.insert_one.return_value = AsyncMock()
    mock_db.call_sessions.insert_one.return_value.inserted_id = ObjectId()
    
    mock_db.call_sessions.find_one.return_value = {
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
    }
    
    mock_db.call_sessions.update_one.return_value = AsyncMock()
    mock_db.call_sessions.update_one.return_value.modified_count = 1
    
    return mock_db

@pytest.mark.asyncio
async def test_voice_screen_candidate(mock_database):
    """Test voice screening candidate with Ultravox API."""
    # Mock the get_database function to return our mock database
    with patch('app.services.candidates.get_database', return_value=mock_database):
        # Mock Twilio client
        with patch('twilio.rest.Client', return_value=AsyncMock()) as mock_twilio:
            # Configure Twilio mock
            mock_twilio.return_value.calls.create.return_value = MOCK_TWILIO_CALL
            
            # Mock httpx client for Ultravox API calls
            with patch('httpx.AsyncClient') as mock_httpx:
                # Configure mock response for Ultravox API
                mock_httpx.return_value.__aenter__.return_value.post.return_value.status_code = 200
                mock_httpx.return_value.__aenter__.return_value.post.return_value.json.return_value = MOCK_ULTRAVOX_RESPONSE
                
                # Call the function being tested
                result = await voice_screen_candidate(
                    job_id=MOCK_JOB_ID,
                    candidate_id=MOCK_CANDIDATE_ID,
                    current_user=MOCK_USER
                )
                
                # Verify the results
                assert result["call_id"] == "mock-call-123"
                assert result["ultravox_call_id"] == "mock-call-123"
                assert result["status"] == "initiated"
                
                # Verify database updates
                mock_database.candidates.update_one.assert_called_once()
                mock_database.call_sessions.insert_one.assert_called_once()

@pytest.mark.asyncio
async def test_process_call_results(mock_database):
    """Test processing call results with notice period update."""
    
    # Mock for the Ultravox call details API response - including notice period
    mock_call_details = {
        "callId": "mock-call-123",
        "status": "completed",
        "summary": "The candidate is available with notice period of 2 months.",
        "score": 85.0,
        "notice_period": "2 months",
        "current_compensation": "Not specified",
        "expected_compensation": "Not specified"
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
                "text": "Thank you for that information. I'll update our records with your 2 month notice period."
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
            mock_client.get.side_effect = [
                # First call - get call details
                AsyncMock(
                    status_code=200,
                    json=AsyncMock(return_value=mock_call_details),
                    raise_for_status=AsyncMock()
                ),
                # Second call - get messages for transcript
                AsyncMock(
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
            
            # Verify database updates - candidate record should be updated with notice period
            mock_database.candidates.update_one.assert_called_once()
            args, kwargs = mock_database.candidates.update_one.call_args
            
            # Check that the notice_period field is being set to "2 months"
            assert kwargs["$set"]["notice_period"] == "2 months"
            
            # Check that screening_in_progress is set to False
            assert kwargs["$set"]["screening_in_progress"] is False
            
            # Verify job statistics update
            mock_database.jobs.update_one.assert_called_once()
            
            # Verify call session update
            mock_database.call_sessions.update_one.assert_called_once() 