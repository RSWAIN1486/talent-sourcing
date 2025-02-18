from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Response
from fastapi.responses import StreamingResponse
from app.models.api import CandidateResponse
from app.models.database import User
from app.services.candidates import (
    upload_resume,
    get_candidates,
    get_candidate,
    delete_candidate,
    get_resume_file
)
from app.api.deps import get_current_user
import os
import logging
from io import BytesIO

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/{job_id}/upload", response_model=CandidateResponse)
async def create_upload_file(
    job_id: str,
    file: UploadFile,
    current_user: User = Depends(get_current_user)
):
    """
    Upload a resume file (PDF or ZIP containing PDFs)
    """
    return await upload_resume(job_id, file, current_user)

@router.get("/{job_id}/candidates", response_model=List[CandidateResponse])
async def list_candidates(
    job_id: str,
    skip: int = 0,
    limit: int = 10,
    current_user: User = Depends(get_current_user)
):
    """
    List all candidates for a job
    """
    return await get_candidates(job_id, skip, limit)

@router.get("/{job_id}/candidates/{candidate_id}", response_model=CandidateResponse)
async def get_candidate_details(
    job_id: str,
    candidate_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get details of a specific candidate
    """
    candidate = await get_candidate(job_id, candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return candidate

@router.get("/{job_id}/candidates/{candidate_id}/resume")
async def download_resume(
    job_id: str,
    candidate_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Download a candidate's resume
    """
    logger.info(f"Download request for job_id: {job_id}, candidate_id: {candidate_id}")
    
    try:
        content, filename = await get_resume_file(candidate_id)
        
        return StreamingResponse(
            BytesIO(content),
            media_type="application/pdf",
            headers={
                'Content-Disposition': f'attachment; filename="{filename}"',
                'Access-Control-Expose-Headers': 'Content-Disposition'
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error serving file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error serving file: {str(e)}")

@router.delete("/{job_id}/candidates/{candidate_id}")
async def remove_candidate(
    job_id: str,
    candidate_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Delete a candidate
    """
    try:
        await delete_candidate(candidate_id)
        return {"status": "success"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting candidate: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))