import logging
import httpx
import json
from typing import Dict, Any, Optional
from app.core.config import settings

logger = logging.getLogger(__name__)

class UltravoxClient:
    """Client for interacting with the Ultravox AI Voice API"""
    
    def __init__(self, api_key: str, api_base_url: str):
        """
        Initialize the Ultravox client
        
        Args:
            api_key: API key for authentication
            api_base_url: Base URL for the Ultravox API
        """
        self.api_key = api_key
        self.api_base_url = api_base_url
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
    
    async def create_agent(self, system_prompt: str, job_description: str) -> Dict[str, Any]:
        """
        Create a voice agent in Ultravox
        
        Args:
            system_prompt: System prompt for the agent
            job_description: Job description to inform the agent
            
        Returns:
            Dict containing the agent ID and other information
        """
        try:
            async with httpx.AsyncClient() as client:
                payload = {
                    "system_prompt": system_prompt,
                    "description": job_description,
                    "voice_id": "echo",  # Default voice
                    "name": f"Recruitment Agent - {job_description[:30]}..."
                }
                
                response = await client.post(
                    f"{self.api_base_url}/agents",
                    headers=self.headers,
                    json=payload,
                    timeout=30.0
                )
                
                response.raise_for_status()
                return await response.json()
                
        except Exception as e:
            logger.error(f"Error creating Ultravox agent: {str(e)}")
            raise
    
    async def get_call_status(self, call_id: str) -> Dict[str, Any]:
        """
        Get the status of a call
        
        Args:
            call_id: The ID of the call
            
        Returns:
            Dict containing call status information
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.api_base_url}/calls/{call_id}",
                    headers=self.headers,
                    timeout=30.0
                )
                
                response.raise_for_status()
                return await response.json()
                
        except Exception as e:
            logger.error(f"Error getting call status: {str(e)}")
            raise
    
    async def get_call_transcript(self, call_id: str) -> Dict[str, Any]:
        """
        Get the transcript of a call
        
        Args:
            call_id: The ID of the call
            
        Returns:
            Dict containing the call transcript
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.api_base_url}/calls/{call_id}/transcript",
                    headers=self.headers,
                    timeout=30.0
                )
                
                response.raise_for_status()
                return await response.json()
                
        except Exception as e:
            logger.error(f"Error getting call transcript: {str(e)}")
            raise
    
    async def analyze_call(self, call_id: str, transcript: str) -> Dict[str, Any]:
        """
        Analyze a call transcript
        
        Args:
            call_id: The ID of the call
            transcript: The call transcript
            
        Returns:
            Dict containing analysis results
        """
        try:
            async with httpx.AsyncClient() as client:
                payload = {
                    "transcript": transcript,
                    "analysis_type": "candidate_screening"
                }
                
                response = await client.post(
                    f"{self.api_base_url}/calls/{call_id}/analyze",
                    headers=self.headers,
                    json=payload,
                    timeout=30.0
                )
                
                response.raise_for_status()
                return await response.json()
                
        except Exception as e:
            logger.error(f"Error analyzing call: {str(e)}")
            raise

async def analyze_call_transcript(transcript: str) -> Dict[str, Any]:
    """
    Analyze a call transcript using the Ultravox API
    
    Args:
        transcript: The call transcript text
        
    Returns:
        Dict with analysis results
    """
    if not transcript:
        logger.warning("Empty transcript provided for analysis")
        return {
            "success": False,
            "error": "Empty transcript"
        }
    
    try:
        # In production, this would make an actual API call
        # For now, we'll simulate the response
        return await _simulate_ultravox_response(transcript)
        
        # The real implementation would look like this:
        """
        async with httpx.AsyncClient() as client:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {settings.ULTRAVOX_API_KEY}"
            }
            
            payload = {
                "transcript": transcript,
                "analysis_type": "candidate_screening"
            }
            
            response = await client.post(
                f"{settings.ULTRAVOX_API_BASE_URL}/v1/analyze",
                headers=headers,
                json=payload
            )
            
            if response.status_code != 200:
                error_text = response.text
                logger.error(f"Ultravox API error: {error_text}")
                return {
                    "success": False,
                    "error": f"API error: {response.status_code}",
                    "details": error_text
                }
            
            result = await response.json()
            return {
                "success": True,
                "screening_score": result.get("candidate_score", 0),
                "screening_summary": result.get("summary", ""),
                "notice_period": result.get("notice_period", ""),
                "current_compensation": result.get("current_compensation", ""),
                "expected_compensation": result.get("expected_compensation", "")
            }
        """
    except Exception as e:
        logger.error(f"Error analyzing transcript: {str(e)}")
        return {
            "success": False,
            "error": f"Analysis error: {str(e)}"
        }

async def _simulate_ultravox_response(transcript: str) -> Dict[str, Any]:
    """
    Simulates a response from the Ultravox API for testing
    
    Args:
        transcript: The call transcript
        
    Returns:
        Dict with simulated analysis results
    """
    # Extract insights based on keywords in the transcript
    # This is a very simplified simulation
    
    score = 85  # Default score
    
    # Adjust score based on keywords
    if "experience" in transcript.lower():
        score += 5
    if "degree" in transcript.lower() or "education" in transcript.lower():
        score += 3
    if "project" in transcript.lower() or "developed" in transcript.lower():
        score += 4
    if "team" in transcript.lower() or "collaboration" in transcript.lower():
        score += 3
    
    # Cap the score at 100
    score = min(score, 100)
    
    # Extract notice period if mentioned
    notice_period = "30 days"  # Default
    if "two weeks" in transcript.lower() or "14 days" in transcript.lower():
        notice_period = "14 days"
    elif "one month" in transcript.lower() or "30 days" in transcript.lower():
        notice_period = "30 days"
    elif "immediate" in transcript.lower() or "right away" in transcript.lower():
        notice_period = "Immediate"
    
    # Extract compensation information if mentioned
    current_comp = "$90,000"  # Default
    expected_comp = "$110,000"  # Default
    
    # In a real implementation, we would use more sophisticated NLP to extract this information
    
    return {
        "success": True,
        "screening_score": score,
        "screening_summary": "The candidate has relevant experience and seems to be a good fit for the role. They articulate their skills well and have the necessary qualifications for the position.",
        "notice_period": notice_period,
        "current_compensation": current_comp,
        "expected_compensation": expected_comp
    } 