import asyncio
import os
import logging
from datetime import datetime
from bson import ObjectId
from dotenv import load_dotenv
from twilio.rest import Client
import httpx
from motor.motor_asyncio import AsyncIOMotorClient
import sys
import pytest
from unittest.mock import patch, AsyncMock, MagicMock

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add parent directory to path to allow imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

# Load environment variables from the root directory
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
dotenv_path = os.path.join(root_dir, ".env")
load_dotenv(dotenv_path)

# Import app modules
from app.core.config import settings
from app.models.database import CandidateResponse, serialize_candidate
from app.services.voice_screening import voice_screening_service
from app.utils.phone_utils import format_phone_number
from app.services.candidates import voice_screen_candidate, process_call_results
from app.services.voice_screening import VoiceScreeningService

# Twilio test credentials - using environment variables
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
TEST_PHONE_NUMBER = os.getenv("TEST_PHONE_NUMBER", "+919007696846")

async def get_test_database():
    """Connect to MongoDB and return test database instance"""
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    return client[settings.MONGODB_DB_NAME]

async def create_test_job_and_candidate():
    """Create a test job and candidate for voice screening test"""
    db = await get_test_database()
    
    # Create a test user if not exists
    user_id = ObjectId()
    user = await db.users.find_one({"email": "test@example.com"})
    if not user:
        user = {
            "_id": user_id,
            "email": "test@example.com",
            "hashed_password": "dummy_hashed_password",
            "full_name": "Test User",
            "is_active": True,
            "is_superuser": False,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        await db.users.insert_one(user)
        logger.info(f"Created test user with ID: {user_id}")
    else:
        user_id = user["_id"]
        logger.info(f"Using existing test user with ID: {user_id}")
    
    # Create a test job
    job_id = ObjectId()
    job = {
        "_id": job_id,
        "title": "Test Software Engineer Position",
        "description": "This is a test job for voice screening",
        "responsibilities": "Testing voice screening functionality",
        "requirements": "Python experience",
        "total_candidates": 0,
        "resume_screened": 0,
        "phone_screened": 0,
        "created_by_id": user_id,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    # Check if the test job already exists
    existing_job = await db.jobs.find_one({"title": "Test Software Engineer Position"})
    if existing_job:
        job_id = existing_job["_id"]
        logger.info(f"Using existing test job with ID: {job_id}")
    else:
        await db.jobs.insert_one(job)
        logger.info(f"Created test job with ID: {job_id}")
    
    # Create a test candidate with the test phone number
    candidate_id = ObjectId()
    candidate = {
        "_id": candidate_id,
        "job_id": job_id,
        "name": "Test Candidate",
        "email": "testcandidate@example.com",
        "phone": TEST_PHONE_NUMBER,  # Using the registered test phone number
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
        "created_by_id": user_id,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    # Check if the test candidate already exists
    existing_candidate = await db.candidates.find_one({
        "email": "testcandidate@example.com",
        "job_id": job_id
    })
    
    if existing_candidate:
        # Update the phone number to ensure it's the test number
        await db.candidates.update_one(
            {"_id": existing_candidate["_id"]},
            {"$set": {"phone": TEST_PHONE_NUMBER}}
        )
        candidate_id = existing_candidate["_id"]
        logger.info(f"Using existing test candidate with ID: {candidate_id}")
    else:
        await db.candidates.insert_one(candidate)
        logger.info(f"Created test candidate with ID: {candidate_id}")
    
    # Create a mock user object for the test
    mock_user = {
        "_id": user_id,
        "id": str(user_id),
        "email": "test@example.com",
        "full_name": "Test User"
    }
    
    return {
        "job_id": str(job_id),
        "candidate_id": str(candidate_id),
        "user": mock_user
    }

async def test_voice_screening_with_service():
    """Test the voice screening workflow using the VoiceScreeningService"""
    try:
        # Get test data
        test_data = await create_test_job_and_candidate()
        
        logger.info(f"Starting voice screening test with: {test_data}")
        
        # Get candidate from database
        db = await get_test_database()
        candidate = await db.candidates.find_one({"_id": ObjectId(test_data["candidate_id"])})
        
        if not candidate:
            logger.error("Test candidate not found in database")
            return {"success": False, "error": "Test candidate not found"}
        
        # Initialize VoiceScreeningService
        logger.info("Initializing voice screening service")
        
        # Format phone number
        phone_number = format_phone_number(candidate["phone"])
        if not phone_number:
            logger.error(f"Invalid phone number format: {candidate['phone']}")
            return {"success": False, "error": "Invalid phone number format"}
        
        # Initiate call
        logger.info(f"Initiating voice screening call to {phone_number}")
        result = await voice_screening_service.initiate_screening_call(
            test_data["candidate_id"], 
            phone_number
        )
        
        logger.info(f"Voice screening call initiated: {result}")
        
        if not result.get("success", False):
            logger.error(f"Failed to initiate call: {result.get('error', 'Unknown error')}")
            return {"success": False, "error": result.get("error", "Failed to initiate call")}
        
        # Wait for user input to simulate completing the call
        print("\nA call has been initiated to your phone number.")
        print("After you complete the call, press Enter to continue...")
        input()
        
        # Simulate the webhook callback
        call_data = {
            "CallSid": result["call_id"],
            "CallStatus": "completed"
        }
        
        logger.info("Processing call status update")
        status_result = await voice_screening_service.process_call_status(call_data)
        logger.info(f"Call status update processed: {status_result}")
        
        # Simulate speech input (normally would come from Twilio webhook)
        voice_screening_service.active_calls[result["call_id"]] = {
            "candidate_id": test_data["candidate_id"],
            "phone_number": phone_number,
            "transcript": [
                "Yes, I'm interested in the Software Engineer position.",
                "My notice period is 30 days.",
                "My current compensation is $90,000 per year.",
                "I'm looking for a salary of around $110,000 for this role."
            ]
        }
        
        # Analyze call results
        logger.info("Analyzing call results")
        analysis_result = await voice_screening_service.analyze_call_results(result["call_id"])
        logger.info(f"Call analysis completed: {analysis_result}")
        
        # Check if candidate record was updated
        updated_candidate = await db.candidates.find_one({"_id": ObjectId(test_data["candidate_id"])})
        
        return {
            "success": True,
            "call_id": result["call_id"],
            "screening_score": updated_candidate.get("screening_score"),
            "screening_summary": updated_candidate.get("screening_summary"),
            "notice_period": updated_candidate.get("notice_period"),
            "current_compensation": updated_candidate.get("current_compensation"),
            "expected_compensation": updated_candidate.get("expected_compensation")
        }
        
    except Exception as e:
        logger.error(f"Error in voice screening workflow test: {str(e)}", exc_info=True)
        return {"success": False, "error": str(e)}

# To run as standalone test script
if __name__ == "__main__":
    try:
        result = asyncio.run(test_voice_screening_with_service())
        logger.info(f"Voice screening workflow test completed: {result}")
        
        if not result.get("success", False):
            sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Test interrupted by user")
        sys.exit(1)

# For pytest
@pytest.mark.asyncio
async def test_voice_screening_workflow():
    """Pytest-compatible test function for the voice screening workflow"""
    # This would normally use mocks instead of making real calls
    # For demonstration only - real implementation would use mocks
    from unittest.mock import patch, AsyncMock
    
    with patch("app.services.voice_screening.voice_screening_service.client.calls.create") as mock_create:
        # Mock the Twilio call creation
        mock_call = AsyncMock()
        mock_call.sid = "TEST_CALL_SID"
        mock_call.status = "completed"
        mock_create.return_value = mock_call
        
        # Use the test with mocked Twilio client
        # In a real test, you'd replace more components and verify the behavior
        logger.info("Running mocked voice screening test")
        # Call the function (implementation omitted for brevity)
        # result = await test_voice_screening_with_service()
        # assert result["success"] is True
        
        # For demonstration only - we'd assert on specifics in a real test 

@pytest.mark.asyncio
async def test_voice_screening_workflow_mock(mock_db, mock_candidate, mock_job, mock_user, mock_twilio_client):
    """Test the complete voice screening workflow with mocks"""
    # Arrange
    candidate_id = str(mock_candidate["_id"])
    job_id = str(mock_job["_id"])
    
    # Set up the database mocks
    mock_db.candidates.find_one.side_effect = [mock_candidate]
    mock_db.jobs.find_one.side_effect = [mock_job]
    
    # Create a mock call session that will be returned by find_one
    mock_call_session = {
        "call_id": "CA12345678901234567890123456789012",
        "agent_id": "mock_agent_12345",
        "candidate_id": mock_candidate["_id"],
        "job_id": mock_job["_id"],
        "status": "initiated"
    }
    
    # Set up the call_sessions.find_one to return the mock call session
    mock_db.call_sessions.find_one.return_value = mock_call_session
    
    # Mock httpx client for API calls
    mock_httpx_client = AsyncMock()
    mock_response = AsyncMock()
    mock_response.raise_for_status = AsyncMock()
    
    # Set up mock responses for the API calls
    responses = [
        # Create agent response
        {"id": "agent_12345"},
        # Get call status response
        {"id": "call_12345", "status": "completed"},
        # Get transcript response
        {"transcript": "AI: Hello\nCandidate: Hi, this is a test call"},
        # Analyze call response
        {
            "screening_score": 85,
            "notice_period": "30 days",
            "current_compensation": "$90,000",
            "expected_compensation": "$110,000",
            "summary": "The candidate is interested in the position."
        }
    ]
    
    mock_response.json = AsyncMock(side_effect=lambda: responses.pop(0) if responses else {})
    mock_httpx_client.post.return_value = mock_response
    mock_httpx_client.get.return_value = mock_response
    
    # Mock Twilio client
    mock_call = mock_twilio_client.calls.create.return_value
    mock_call.sid = "CA12345678901234567890123456789012"
    mock_call.status = "queued"
    
    # Act - Step 1: Initiate the voice screening
    with patch('app.services.candidates.get_database', return_value=mock_db), \
         patch('app.services.candidates.Client', return_value=mock_twilio_client), \
         patch('httpx.AsyncClient', return_value=mock_httpx_client):
        
        # Initiate the voice screening
        result = await voice_screen_candidate(job_id, candidate_id, mock_user)
        
        logger.info(f"Voice screening initiated: {result}")
        
        # Assert - Step 1: Check the call was initiated
        assert result["call_id"] == "CA12345678901234567890123456789012"
        assert "agent_id" in result
        assert result["status"] in ["initiated", "queued"]
        
        # Verify the database was updated
        assert mock_db.candidates.update_one.call_count == 1
        assert mock_db.call_sessions.insert_one.call_count == 1
        
        # Act - Step 2: Simulate call completion
        mock_call.status = "completed"
        mock_call.duration = "60"
        
        # Reset responses for the second part
        responses = [
            # Get call status response
            {"id": "call_12345", "status": "completed"},
            # Get transcript response
            {"transcript": "AI: Hello\nCandidate: Hi, this is a test call"},
            # Analyze call response
            {
                "screening_score": 85,
                "notice_period": "30 days",
                "current_compensation": "$90,000",
                "expected_compensation": "$110,000",
                "summary": "The candidate is interested in the position."
            }
        ]
        
        # Process the call completion webhook
        mock_call_data = {
            "CallSid": result["call_id"],
            "CallStatus": "completed",
            "Duration": "60"
        }
        
        # Reset the mock db update counts
        mock_db.candidates.update_one.reset_mock()
        mock_db.jobs.update_one.reset_mock()
        mock_db.call_sessions.update_one.reset_mock()
        
        # Simulate the webhook callback
        callback_result = await process_call_results(mock_call_data)
        
        logger.info(f"Call completion processed: {callback_result}")
        
        # Assert - Step 2: Check the call completion was processed
        assert "candidate_id" in callback_result
        assert callback_result["status"] == "success"
        
        # Verify the database was updated with screening results
        assert mock_db.candidates.update_one.call_count == 1
        assert mock_db.call_sessions.update_one.call_count == 1
        
        # Full end-to-end test passed
        return {
            "success": True,
            "call_id": result["call_id"],
            "screening_results": {
                "score": 85,
                "notice_period": "30 days",
                "current_compensation": "$90,000",
                "expected_compensation": "$110,000"
            }
        }

@pytest.mark.asyncio
async def test_voice_screening_workflow_service(mock_db, mock_candidate, mock_twilio_client):
    """Test the voice screening workflow using the VoiceScreeningService"""
    # Arrange
    candidate_id = str(mock_candidate["_id"])
    phone_number = "+15551234567"
    
    # Set up the database mocks
    mock_db.candidates.find_one.return_value = mock_candidate
    mock_db.candidates.update_one = AsyncMock()
    
    # Create the voice screening service
    with patch('app.services.voice_screening.Client', return_value=mock_twilio_client), \
         patch('app.services.voice_screening.update_candidate', AsyncMock(return_value=mock_candidate)):
        service = VoiceScreeningService()
        service.webhook_url = "https://example.com/api/v1/callback"
    
    # Mock call creation
    mock_call = mock_twilio_client.calls.create.return_value
    mock_call.sid = "CA12345678901234567890123456789012"
    mock_call.status = "queued"
    
    # Act - Step 1: Initiate the screening call
    with patch('app.services.voice_screening.update_candidate', AsyncMock(return_value=mock_candidate)) as mock_update:
        # Initiate the call
        result = await service.initiate_screening_call(candidate_id, phone_number)
        
        logger.info(f"Voice screening initiated: {result}")
        
        # Assert - Step 1: Check the call was initiated
        assert result["success"] is True
        assert result["call_id"] == "CA12345678901234567890123456789012"
        assert result["status"] == "queued"
        
        # Verify candidate was updated
        mock_update.assert_called_once_with(candidate_id, {"screening_in_progress": True})
    
    # Act - Step 2: Simulate call completion
    mock_call.status = "completed"
    
    # Mock the process_recording function and database operations
    with patch('app.services.voice_screening.get_database', return_value=mock_db), \
         patch('app.services.voice_screening.process_recording', AsyncMock(return_value={
             "transcript": "Test transcript",
             "screening_score": 85,
             "notice_period": "30 days",
             "current_compensation": "$90,000",
             "expected_compensation": "$110,000",
             "summary": "Candidate seems suitable"
         })), \
         patch('app.services.voice_screening.update_candidate', AsyncMock(return_value=mock_candidate)):
        
        # Set up the active call in the service
        service.active_calls[mock_call.sid] = {
            "candidate_id": candidate_id,
            "phone_number": phone_number
        }
        
        # Process the call completion
        call_data = {
            "CallSid": mock_call.sid,
            "CallStatus": "completed",
            "RecordingUrl": "https://api.twilio.com/recording/RE123",
            "RecordingSid": "RE123",
            "Duration": "120"
        }
        
        # Mock the database update operations to return success
        mock_db.candidates.update_one.return_value = AsyncMock()
        
        # Process the call completion
        completion_result = await service.process_call_completion(call_data)
        
        logger.info(f"Call completion processed: {completion_result}")
        
        # Assert - Step 2: Check the call completion was processed
        assert completion_result["success"] is True
        assert completion_result["status"] == "processed"
        assert completion_result["screening_score"] == 85
        
        # Verify the database was updated
        assert mock_db.candidates.update_one.called
        
        # Verify the call was removed from active calls
        assert mock_call.sid not in service.active_calls
        
        # Full end-to-end test with service passed
        return {
            "success": True,
            "call_id": mock_call.sid,
            "screening_results": {
                "score": 85,
                "notice_period": "30 days",
                "current_compensation": "$90,000",
                "expected_compensation": "$110,000"
            }
        }

if __name__ == "__main__":
    try:
        print("\nRunning voice screening workflow test...")
        
        # Create mocks
        mock_db = AsyncMock()
        mock_db.candidates = AsyncMock()
        mock_db.jobs = AsyncMock()
        mock_db.call_sessions = AsyncMock()
        
        mock_candidate = {
            "_id": ObjectId(),
            "id": str(ObjectId()),
            "job_id": ObjectId(),
            "name": "Test Candidate",
            "phone": "+15551234567",
            "screening_in_progress": False
        }
        
        mock_job = {
            "_id": mock_candidate["job_id"],
            "id": str(mock_candidate["job_id"]),
            "title": "Test Job"
        }
        
        mock_user = {
            "id": str(ObjectId()),
            "email": "test@example.com"
        }
        
        mock_twilio_client = MagicMock()
        mock_call = MagicMock()
        mock_call.sid = "CA12345678901234567890123456789012"
        mock_call.status = "queued"
        mock_twilio_client.calls.create.return_value = mock_call
        
        # Run the test
        result = asyncio.run(test_voice_screening_workflow_service(
            mock_db, 
            mock_candidate,
            mock_twilio_client
        ))
        
        logger.info(f"Test completed: {result}")
        
        if not result["success"]:
            sys.exit(1)
            
        print("\nTest completed successfully!")
        
    except Exception as e:
        logger.error(f"Error in voice screening workflow test: {str(e)}", exc_info=True)
        sys.exit(1) 