from fastapi import APIRouter, Depends, HTTPException, Request, Body
from typing import Dict, Any
import logging
import json

from app.core.security import get_current_user
from app.models.database import User, get_candidate_by_id
from app.services.voice_screening import voice_screening_service
from app.utils.phone_utils import format_phone_number

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/screen/{candidate_id}", response_model=Dict[str, Any])
async def initiate_voice_screening(
    candidate_id: str,
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Initiate a voice screening call to a candidate
    """
    # Check if the candidate exists
    candidate = await get_candidate_by_id(candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    # Check if the candidate has a phone number
    if not candidate.phone:
        raise HTTPException(status_code=400, detail="Candidate does not have a phone number")
    
    # Format the phone number to E.164 format
    formatted_phone = format_phone_number(candidate.phone)
    if not formatted_phone:
        raise HTTPException(
            status_code=400, 
            detail="Invalid phone number format. Please ensure the number includes country code."
        )
    
    # Check if a screening is already in progress
    if getattr(candidate, "screening_in_progress", False):
        raise HTTPException(
            status_code=400,
            detail="A screening call is already in progress for this candidate"
        )
    
    # Initiate the call
    result = await voice_screening_service.initiate_screening_call(candidate_id, formatted_phone)
    
    if not result.get("success", False):
        # If there was an error, return it with an appropriate status code
        raise HTTPException(
            status_code=500,
            detail=result.get("error", "Unknown error occurred while initiating the call")
        )
    
    return result

@router.post("/status/{candidate_id}", response_model=Dict[str, Any])
async def get_screening_status(
    candidate_id: str,
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get the status of a voice screening for a candidate
    """
    # Check if the candidate exists
    candidate = await get_candidate_by_id(candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    # Return the screening status
    return {
        "candidate_id": candidate_id,
        "screening_in_progress": getattr(candidate, "screening_in_progress", False),
        "screening_score": getattr(candidate, "screening_score", None),
        "screening_summary": getattr(candidate, "screening_summary", None),
        "notice_period": getattr(candidate, "notice_period", None),
        "current_compensation": getattr(candidate, "current_compensation", None),
        "expected_compensation": getattr(candidate, "expected_compensation", None)
    }

# Webhook routes - these don't require authentication as they're called by Twilio
@router.post("/webhooks/voice-call/status", response_model=Dict[str, Any])
async def webhook_call_status(request: Request) -> Dict[str, Any]:
    """
    Webhook endpoint for Twilio call status updates
    """
    try:
        # Parse the form data from Twilio
        form_data = await request.form()
        # Convert form data to dict
        data = {key: form_data[key] for key in form_data}
        
        logger.info(f"Received call status webhook: {data}")
        
        # Process the call status
        result = await voice_screening_service.process_call_status(data)
        return result
    except Exception as e:
        logger.error(f"Error processing call status webhook: {str(e)}")
        return {"success": False, "error": str(e)}

@router.post("/webhooks/voice-call/gather", response_model=Dict[str, Any])
async def webhook_call_gather(request: Request) -> Dict[str, Any]:
    """
    Webhook endpoint for Twilio speech gathering
    """
    try:
        # Parse the form data from Twilio
        form_data = await request.form()
        # Convert form data to dict
        data = {key: form_data[key] for key in form_data}
        
        logger.info(f"Received speech input webhook: {data}")
        
        # Process the speech input
        result = await voice_screening_service.process_speech_input(data)
        return result
    except Exception as e:
        logger.error(f"Error processing speech input webhook: {str(e)}")
        return {"success": False, "error": str(e)}

@router.post("/webhooks/voice-call/recording", response_model=Dict[str, Any])
async def webhook_call_recording(request: Request) -> Dict[str, Any]:
    """
    Webhook endpoint for Twilio recording notifications
    """
    try:
        # Parse the form data from Twilio
        form_data = await request.form()
        # Convert form data to dict
        data = {key: form_data[key] for key in form_data}
        
        logger.info(f"Received recording webhook: {data}")
        
        # Process the recording
        result = await voice_screening_service.process_call_recording(data)
        return result
    except Exception as e:
        logger.error(f"Error processing recording webhook: {str(e)}")
        return {"success": False, "error": str(e)}

@router.post("/analyze/{call_sid}", response_model=Dict[str, Any])
async def analyze_call(
    call_sid: str,
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Manually trigger analysis of a completed call
    """
    result = await voice_screening_service.analyze_call_results(call_sid)
    
    if not result.get("success", False):
        # If there was an error, return it with an appropriate status code
        raise HTTPException(
            status_code=500,
            detail=result.get("error", "Unknown error occurred while analyzing the call")
        )
    
    return result 