from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, Body
from app.models.database import create_job, serialize_job
from app.services import jobs
from app.services.auth import get_current_active_user
from app.core.mongodb import get_database
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/")
async def create_new_job(
    job_data: Dict[str, Any] = Body(...),
    current_user: dict = Depends(get_current_active_user)
) -> dict:
    """Create a new job posting"""
    try:
        logger.info(f"Received job creation request. Data: {job_data}")
        logger.info(f"Current user: {current_user}")
        
        # Validate required fields
        required_fields = ["title", "description", "responsibilities", "requirements"]
        for field in required_fields:
            if not job_data.get(field):
                logger.error(f"Missing required field: {field}")
                raise HTTPException(
                    status_code=422,
                    detail=f"{field} is required"
                )
            if not isinstance(job_data[field], str):
                logger.error(f"Field {field} is not a string: {type(job_data[field])}")
                raise HTTPException(
                    status_code=422,
                    detail=f"{field} must be a string"
                )
            job_data[field] = job_data[field].strip()
            if not job_data[field]:
                logger.error(f"Field {field} is empty after stripping")
                raise HTTPException(
                    status_code=422,
                    detail=f"{field} cannot be empty"
                )
                
        logger.info("All fields validated successfully")
        
        # Create the job
        try:
            # Remove any unexpected fields from job_data
            cleaned_data = {
                "title": job_data["title"].strip(),
                "description": job_data["description"].strip(),
                "responsibilities": job_data["responsibilities"].strip(),
                "requirements": job_data["requirements"].strip()
            }
            logger.info(f"Cleaned job data: {cleaned_data}")
            
            # Ensure current_user has required fields
            if not current_user.get("_id"):
                logger.error("Current user missing _id field")
                raise HTTPException(
                    status_code=500,
                    detail="Invalid user data"
                )
            
            job = await jobs.create_job(
                **cleaned_data,
                created_by=current_user
            )
            logger.info(f"Job created successfully: {job}")
            return job
        except Exception as e:
            logger.error(f"Error in jobs.create_job: {str(e)}", exc_info=True)
            raise
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in create_new_job: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@router.get("/")
async def get_jobs(skip: int = 0, limit: int = 10) -> List[dict]:
    return await jobs.get_jobs(skip=skip, limit=limit)

@router.get("/stats")
async def get_job_stats() -> dict:
    """Get overall job statistics"""
    db = get_database()
    
    # Get total jobs
    total_jobs = await db.jobs.count_documents({})
    
    # Get list of existing job IDs
    job_ids = [job["_id"] async for job in db.jobs.find({}, {"_id": 1})]
    
    # Get total candidates from existing jobs only
    total_candidates = await db.candidates.count_documents({"job_id": {"$in": job_ids}})
    
    # Get total resume screened candidates from existing jobs only
    resume_screened = await db.candidates.count_documents({
        "job_id": {"$in": job_ids},
        "resume_score": {"$ne": None}
    })
    
    # Get total phone screened candidates from existing jobs only
    phone_screened = await db.candidates.count_documents({
        "job_id": {"$in": job_ids},
        "screening_score": {"$ne": None}
    })
    
    return {
        "total_jobs": total_jobs,
        "total_candidates": total_candidates,
        "resume_screened": resume_screened,
        "phone_screened": phone_screened
    }

@router.get("/{job_id}")
async def get_job(job_id: str) -> dict:
    job = await jobs.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return serialize_job(job)

@router.put("/{job_id}")
async def update_job(
    job_id: str,
    job_data: Dict[str, Any] = Body(...),
    current_user: dict = Depends(get_current_active_user)
) -> dict:
    job = await jobs.update_job(
        job_id=job_id,
        title=job_data.get("title"),
        description=job_data.get("description"),
        responsibilities=job_data.get("responsibilities"),
        requirements=job_data.get("requirements")
    )
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@router.delete("/{job_id}")
async def delete_job(
    job_id: str,
    current_user: dict = Depends(get_current_active_user)
) -> dict:
    deleted = await jobs.delete_job(job_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Job not found")
    return {"message": "Job deleted successfully"}

@router.post("/{job_id}/sync-candidates")
async def sync_job_candidates(
    job_id: str,
    current_user: dict = Depends(get_current_active_user)
) -> dict:
    """Sync job's candidate count with actual number of candidates"""
    try:
        logger.info(f"Syncing candidates for job {job_id}")
        job = await jobs.sync_job_candidates_count(job_id)
        if not job:
            logger.error(f"Job {job_id} not found")
            raise HTTPException(status_code=404, detail="Job not found")
        logger.info(f"Successfully synced candidates for job {job_id}")
        return job
    except Exception as e:
        logger.error(f"Error syncing job candidates: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 