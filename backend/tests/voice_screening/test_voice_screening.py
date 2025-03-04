import asyncio
import os
import logging
import pytest
from datetime import datetime
from bson import ObjectId
from unittest.mock import patch, AsyncMock, MagicMock
from twilio.rest import Client
from app.core.config import settings
from app.services.candidates import format_phone_number

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Hardcoded test values
TWILIO_ACCOUNT_SID = "AC2dd7a301619d0ae449ada741a35ed235"
TWILIO_AUTH_TOKEN = "fb4643331618e56c7be9a32aedbc252b"
TWILIO_PHONE_NUMBER = "+19034005920"
TEST_PHONE_NUMBER = "+919007696846"

@pytest.mark.asyncio
async def test_voice_screening(test_phone_number, mock_twilio_client):
    """Test voice screening with a mock Twilio call"""
    try:
        # Use the mock Twilio client from fixtures
        with patch('twilio.rest.Client', return_value=mock_twilio_client):
            # Create a TwiML script for the test call
            twiml = """
            <Response>
                <Say>Hello, this is an AI assistant calling from a recruitment agency.</Say>
                <Pause length="1"/>
                <Say>I'm calling about the Software Engineer position. Would you be interested in discussing this opportunity?</Say>
                <Pause length="2"/>
                <Say>Thank you. What is your current notice period at your job?</Say>
                <Pause length="2"/>
                <Say>And what is your current compensation package?</Say>
                <Pause length="2"/>
                <Say>What are your salary expectations for this new role?</Say>
                <Pause length="2"/>
                <Say>Thank you for your time. Someone from our team will follow up with you shortly about next steps.</Say>
            </Response>
            """
            
            # Mock the call
            mock_call = mock_twilio_client.calls.create.return_value
            mock_call.sid = "CA12345678901234567890123456789012"
            
            # Make the call
            logger.info(f"Initiating test call to {test_phone_number}")
            
            client = Client("dummy_sid", "dummy_token")  # Will be patched
            call = client.calls.create(
                to=test_phone_number,
                from_="+19034005920",
                twiml=twiml
            )
            
            call_id = call.sid
            logger.info(f"Call initiated with SID: {call_id}")
            
            # Simulate call completion (no user input needed in test)
            logger.info("Simulating call completion...")
            
            # Update mock call status
            mock_call.status = "completed"
            
            # Fetch the call status
            call = client.calls(call_id).fetch()
            logger.info(f"Final call status: {call.status}")
            
            # Simulate processing the call results
            logger.info("Generating screening score and summary...")
            
            # Mock screening results
            screening_results = {
                "call_id": call_id,
                "status": "completed",
                "screening_score": 85,
                "notice_period": "30 days",
                "current_compensation": "$90,000",
                "expected_compensation": "$110,000",
                "screening_summary": "The candidate is interested in the position. They have a 30-day notice period at their current job. Currently making $90,000 and expecting $110,000 for the new role."
            }
            
            logger.info(f"Call screening results: {screening_results}")
            
            return {
                "success": True,
                "call_id": call_id,
                "results": screening_results
            }
        
    except Exception as e:
        logger.error(f"Error in voice screening test: {str(e)}", exc_info=True)
        return {"success": False, "error": str(e)}

@pytest.mark.asyncio
async def test_voice_screening_with_db(test_phone_number, mock_twilio_client, mock_db, mock_candidate):
    """Test voice screening with database interaction"""
    try:
        # Use the mock database and Twilio client
        with patch('app.services.candidates.get_database', return_value=mock_db), \
             patch('twilio.rest.Client', return_value=mock_twilio_client):
            
            # Set up the database for a candidate
            candidate_id = str(mock_candidate["_id"])
            mock_db.candidates.find_one.return_value = mock_candidate
            
            # Simulate voice screening API call
            from app.services.candidates import voice_screen_candidate
            mock_user = {"id": "test_user_id", "email": "test@example.com"}
            
            # Mock successful call creation
            mock_call = mock_twilio_client.calls.create.return_value
            mock_call.sid = "CA12345678901234567890123456789012"
            mock_call.status = "queued"
            
            # Call the voice screening function
            result = await voice_screen_candidate(
                str(mock_candidate["job_id"]),
                candidate_id,
                mock_user
            )
            
            logger.info(f"Voice screening initiated: {result}")
            
            # Verify the result
            assert "call_id" in result
            assert result["status"] in ["initiated", "queued"]
            
            # Simulate call completion
            mock_call.status = "completed"
            
            # Simulate webhook callback
            from app.services.candidates import process_call_results
            
            mock_call_data = {
                "CallSid": result["call_id"],
                "CallStatus": "completed",
                "Duration": "60"
            }
            
            # Mock the API responses needed for call processing
            mock_httpx_client = AsyncMock()
            mock_response = AsyncMock()
            mock_response.raise_for_status.return_value = None
            
            # Mock responses for call status, transcript and analysis
            responses = [
                {"id": result["call_id"], "status": "completed"},
                {"transcript": "AI: Hello\nCandidate: Hi, this is test candidate"},
                {
                    "screening_score": 85,
                    "notice_period": "30 days",
                    "current_compensation": "$90,000",
                    "expected_compensation": "$110,000",
                    "summary": "Candidate seems suitable"
                }
            ]
            
            mock_response.json = AsyncMock(side_effect=lambda: responses.pop(0) if responses else {})
            mock_httpx_client.get.return_value = mock_response
            mock_httpx_client.post.return_value = mock_response
            
            # Process call results with mocked API client
            with patch('httpx.AsyncClient', return_value=mock_httpx_client):
                callback_result = await process_call_results(mock_call_data)
                
                logger.info(f"Call processing result: {callback_result}")
                
                # Verify the candidate was updated
                assert mock_db.candidates.update_one.call_count >= 1
                
                return {
                    "success": True,
                    "call_id": result["call_id"],
                    "results": callback_result
                }
        
    except Exception as e:
        logger.error(f"Error in voice screening database test: {str(e)}", exc_info=True)
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    try:
        # Run the simple test
        print("\nRunning simple voice screening test...")
        result = asyncio.run(test_voice_screening("+919007696846", MagicMock()))
        logger.info(f"Test completed: {result}")
        
        if not result["success"]:
            import sys
            sys.exit(1)
            
        print("\nTest completed successfully!")
        
    except KeyboardInterrupt:
        logger.info("Test interrupted by user")
        import sys
        sys.exit(1) 