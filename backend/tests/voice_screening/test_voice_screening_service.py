import pytest
import sys
import os
import asyncio
from unittest.mock import patch, AsyncMock, MagicMock
from bson import ObjectId

# Add parent directory to path to allow imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from app.services.voice_screening import VoiceScreeningService

class TestVoiceScreeningService:
    """Test suite for the VoiceScreeningService class"""
    
    @pytest.fixture
    def voice_service(self, mock_twilio_client):
        """Create a VoiceScreeningService instance with mocked dependencies"""
        # Patch the Client constructor to return our mock
        with patch('app.services.voice_screening.Client', return_value=mock_twilio_client):
            # Create the service with test values
            service = VoiceScreeningService()
            # Override webhook URL for testing
            service.webhook_url = "https://example.com/api/v1/callback"
            return service
    
    @pytest.mark.asyncio
    async def test_initiate_screening_call(self, voice_service, mock_candidate, mock_db):
        """Test that initiating a screening call works properly"""
        candidate_id = str(mock_candidate["_id"])
        phone_number = "+15551234567"
        
        # Mock the update_candidate function
        with patch('app.services.voice_screening.update_candidate', AsyncMock()) as mock_update:
            # Call the method under test
            result = await voice_service.initiate_screening_call(candidate_id, phone_number)
            
            # Verify the results
            assert result["success"] is True
            assert "call_id" in result
            assert result["status"] == "initiated"
            
            # Verify candidate was updated
            mock_update.assert_called_once_with(candidate_id, {"screening_in_progress": True})
            
            # Verify Twilio client was called correctly
            voice_service.client.calls.create.assert_called_once()
            call_args = voice_service.client.calls.create.call_args[1]
            assert call_args["to"] == phone_number
            assert call_args["from_"] == voice_service.from_number
            assert "twiml" in call_args
            assert "status_callback" in call_args
            assert call_args["status_callback"] == f"{voice_service.webhook_url}/status"
    
    @pytest.mark.asyncio
    async def test_check_call_status(self, voice_service, mock_twilio_client):
        """Test that checking call status works properly"""
        # Create a test call ID
        call_id = "CA12345678901234567890123456789012"
        
        # Set up the mock call object
        mock_call = MagicMock()
        mock_call.status = "completed"
        mock_call.duration = "60"
        
        # Configure the mock client to return our mock call
        mock_twilio_client.calls.return_value.fetch.return_value = mock_call
        
        # Call the method under test
        result = await voice_service.check_call_status(call_id)
        
        # Verify the results
        assert result["status"] == "completed"
        assert result["duration"] == "60"
        
        # Verify Twilio client was called correctly
        mock_twilio_client.calls.assert_called_once_with(call_id)
        mock_twilio_client.calls.return_value.fetch.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_screening_twiml(self, voice_service):
        """Test that TwiML is correctly generated"""
        # Call the method under test
        twiml = voice_service._create_screening_twiml()
        
        # Verify the TwiML contains expected elements
        assert "<Response>" in twiml
        assert "<Say>" in twiml
        assert "recruitment" in twiml.lower()
        assert "</Response>" in twiml
    
    @pytest.mark.asyncio
    async def test_process_call_recording(self, voice_service, mock_db):
        """Test processing a completed call recording"""
        # Create test call data
        call_data = {
            "CallSid": "CA12345678901234567890123456789012",
            "CallStatus": "completed",
            "RecordingUrl": "https://api.twilio.com/recording/RE123",
            "RecordingSid": "RE123",
            "Duration": "120"
        }
        
        # Mock the database functions
        with patch('app.services.voice_screening.get_database', return_value=mock_db), \
             patch('app.services.voice_screening.process_recording', AsyncMock(return_value={
                 "transcript": "Test transcript",
                 "screening_score": 85,
                 "notice_period": "30 days",
                 "current_compensation": "$90,000",
                 "expected_compensation": "$110,000",
                 "summary": "Candidate seems suitable"
             })):
            
            # Set up the active call in the service
            voice_service.active_calls[call_data["CallSid"]] = {
                "candidate_id": str(ObjectId()),
                "phone_number": "+15551234567"
            }
            
            # Call the method under test
            result = await voice_service.process_call_completion(call_data)
            
            # Verify the results
            assert result["success"] is True
            assert result["status"] == "processed"
            assert "screening_score" in result
            assert result["screening_score"] == 85
            
            # Verify database was updated
            mock_db.candidates.update_one.assert_called_once()
            
            # Verify the call was removed from active calls
            assert call_data["CallSid"] not in voice_service.active_calls 