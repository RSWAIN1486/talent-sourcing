import pytest
import sys
import os
import asyncio
import json
from unittest.mock import patch, AsyncMock, MagicMock
import httpx

# Add parent directory to path to allow imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from app.services.ultravox import UltravoxClient

class TestUltravoxClient:
    """Test suite for the UltravoxClient class"""
    
    @pytest.fixture
    def ultravox_client(self):
        """Create an UltravoxClient instance for testing"""
        client = UltravoxClient(
            api_key="test_api_key",
            api_base_url="https://api.ultravox.example.com"
        )
        return client
    
    @pytest.mark.asyncio
    async def test_create_agent(self, ultravox_client):
        """Test creating a voice agent through the API"""
        # Mock data
        system_prompt = "You are a recruiter for a tech company"
        job_description = "Looking for a senior Python developer"
        expected_result = {"id": "test_id"}
        
        # Create a patched version of httpx.AsyncClient.post that returns our mock response
        async def mock_post(*args, **kwargs):
            mock_response = MagicMock()  # Use MagicMock instead of AsyncMock
            
            # Define raise_for_status as a regular method
            def mock_raise_for_status():
                return None  # No errors to raise
                
            mock_response.raise_for_status = mock_raise_for_status
            
            # Use a real async function for json
            async def mock_json():
                return expected_result
                
            mock_response.json = mock_json
            return mock_response
            
        # Patch just the post method
        with patch('httpx.AsyncClient.post', mock_post):
            # Call the method under test
            result = await ultravox_client.create_agent(system_prompt, job_description)
            
            # Verify the result
            assert result == expected_result
    
    @pytest.mark.asyncio
    async def test_get_call_status(self, ultravox_client):
        """Test retrieving call status through the API"""
        # Mock data
        call_id = "call_12345"
        expected_result = {
            "id": call_id,
            "status": "completed"
        }
        
        # Create a patched version of httpx.AsyncClient.get that returns our mock response
        async def mock_get(*args, **kwargs):
            mock_response = MagicMock()  # Use MagicMock instead of AsyncMock
            
            # Define raise_for_status as a regular method
            def mock_raise_for_status():
                return None  # No errors to raise
                
            mock_response.raise_for_status = mock_raise_for_status
            
            # Use a real async function for json
            async def mock_json():
                return expected_result
                
            mock_response.json = mock_json
            return mock_response
            
        # Patch just the get method
        with patch('httpx.AsyncClient.get', mock_get):
            # Call the method under test
            result = await ultravox_client.get_call_status(call_id)
            
            # Verify the result
            assert result["id"] == call_id
            assert result["status"] == "completed"
    
    @pytest.mark.asyncio
    async def test_get_call_transcript(self, ultravox_client):
        """Test retrieving call transcript through the API"""
        # Mock data
        call_id = "call_12345"
        expected_result = {
            "call_id": call_id,
            "transcript": "AI: Hello\nCandidate: Hi there"
        }
        
        # Create a patched version of httpx.AsyncClient.get that returns our mock response
        async def mock_get(*args, **kwargs):
            mock_response = MagicMock()  # Use MagicMock instead of AsyncMock
            
            # Define raise_for_status as a regular method
            def mock_raise_for_status():
                return None  # No errors to raise
                
            mock_response.raise_for_status = mock_raise_for_status
            
            # Use a real async function for json
            async def mock_json():
                return expected_result
                
            mock_response.json = mock_json
            return mock_response
            
        # Patch just the get method
        with patch('httpx.AsyncClient.get', mock_get):
            # Call the method under test
            result = await ultravox_client.get_call_transcript(call_id)
            
            # Verify the result
            assert result["call_id"] == call_id
            assert "transcript" in result
            assert "AI: Hello" in result["transcript"]
    
    @pytest.mark.asyncio
    async def test_analyze_call(self, ultravox_client):
        """Test analyzing call results through the API"""
        # Mock data
        call_id = "call_12345"
        transcript = "AI: Hello\nCandidate: Hi there"
        expected_result = {
            "call_id": call_id,
            "screening_score": 85,
            "notice_period": "30 days",
            "current_compensation": "$90,000",
            "expected_compensation": "$110,000",
            "summary": "Candidate seems qualified and interested."
        }
        
        # Create a patched version of httpx.AsyncClient.post that returns our mock response
        async def mock_post(*args, **kwargs):
            mock_response = MagicMock()  # Use MagicMock instead of AsyncMock
            
            # Define raise_for_status as a regular method
            def mock_raise_for_status():
                return None  # No errors to raise
                
            mock_response.raise_for_status = mock_raise_for_status
            
            # Use a real async function for json
            async def mock_json():
                return expected_result
                
            mock_response.json = mock_json
            return mock_response
            
        # Patch just the post method
        with patch('httpx.AsyncClient.post', mock_post):
            # Call the method under test
            result = await ultravox_client.analyze_call(call_id, transcript)
            
            # Verify the result
            assert result["call_id"] == call_id
            assert result["screening_score"] == 85
            assert result["notice_period"] == "30 days"
            assert result["current_compensation"] == "$90,000"
            assert result["expected_compensation"] == "$110,000"
            assert result["summary"] == "Candidate seems qualified and interested."
    
    @pytest.mark.asyncio
    async def test_error_handling(self, ultravox_client):
        """Test that API errors are handled properly"""
        # Create a patched version of httpx.AsyncClient.post that raises an exception
        async def mock_post_error(*args, **kwargs):
            raise httpx.HTTPError("API Error")
            
        # Patch just the post method to raise an error
        with patch('httpx.AsyncClient.post', mock_post_error):
            # Call the method and expect an exception
            with pytest.raises(Exception) as exc_info:
                await ultravox_client.create_agent("test prompt", "test description")
            
            # Verify the exception message
            assert "API Error" in str(exc_info.value) 