from datetime import datetime, UTC
from typing import Optional, Dict, Any
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)

class User:
    def __init__(self, **data):
        self._id = data.get("_id")  # Keep the original ObjectId
        self.id = str(data.get("_id", ""))  # String version for API
        self.email = data.get("email", "")
        self.full_name = data.get("full_name", "")
        self.is_active = data.get("is_active", True)
        self.is_superuser = data.get("is_superuser", False)
        self.created_at = data.get("created_at", datetime.now(UTC))
        self.updated_at = data.get("updated_at", datetime.now(UTC))

    def __getitem__(self, key):
        return getattr(self, key)

    @property
    def dict(self):
        """Convert to dictionary for API responses"""
        return {
            "id": self.id,
            "email": self.email,
            "full_name": self.full_name,
            "is_active": self.is_active,
            "is_superuser": self.is_superuser,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

class CandidateResponse:
    def __init__(self, **data):
        self.id = str(data.get("_id", ""))
        self.job_id = str(data.get("job_id", ""))
        self.name = data.get("name", "")
        self.email = data.get("email", "")
        self.phone = data.get("phone")
        self.location = data.get("location")
        self.resume_file_id = str(data.get("resume_file_id", ""))
        self.skills = data.get("skills", {})
        self.resume_score = data.get("resume_score", 0.0)
        self.screening_score = data.get("screening_score")
        self.screening_summary = data.get("screening_summary")
        self.screening_in_progress = data.get("screening_in_progress", False)
        self.call_transcript = data.get("call_transcript")
        self.notice_period = data.get("notice_period")
        self.current_compensation = data.get("current_compensation")
        self.expected_compensation = data.get("expected_compensation")
        self.created_by_id = str(data.get("created_by_id")) if data.get("created_by_id") else None
        self.created_at = data.get("created_at", datetime.now(UTC))
        self.updated_at = data.get("updated_at", datetime.now(UTC))

    @classmethod
    def model_validate(cls, data: dict) -> 'CandidateResponse':
        return cls(**data)

    def __getitem__(self, key):
        return getattr(self, key)

def create_user(email: str, hashed_password: str, full_name: str) -> dict:
    """Create a new user document"""
    return {
        "_id": ObjectId(),
        "email": email,
        "hashed_password": hashed_password,
        "full_name": full_name,
        "is_active": True,
        "is_superuser": False,
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC)
    }

def create_job(
    title: str,
    description: str,
    responsibilities: str,
    requirements: str,
    created_by: dict
) -> dict:
    """Create a job document"""
    logger.info(f"Creating job document with title: {title}")
    logger.info(f"Created by user: {created_by}")
    
    try:
        job = {
            "_id": ObjectId(),
            "title": title,
            "description": description,
            "responsibilities": responsibilities,
            "requirements": requirements,
            "total_candidates": 0,
            "resume_screened": 0,
            "phone_screened": 0,
            "created_by_id": ObjectId(created_by["_id"]),
            "created_at": datetime.now(UTC),
            "updated_at": datetime.now(UTC)
        }
        logger.info(f"Created job document: {job}")
        return job
    except Exception as e:
        logger.error(f"Error creating job document: {str(e)}", exc_info=True)
        raise

def create_candidate(
    job_id: str,
    name: str,
    email: str,
    resume_file_id: str,
    skills: Dict[str, float],
    resume_score: float,
    phone: Optional[str] = None,
    location: Optional[str] = None,
    created_by_id: str = None
) -> dict:
    """Create a candidate document"""
    return {
        "_id": ObjectId(),
        "job_id": ObjectId(job_id),
        "name": name,
        "email": email,
        "phone": phone,
        "location": location,
        "resume_file_id": resume_file_id,
        "skills": skills,
        "resume_score": resume_score,
        "screening_score": None,
        "screening_summary": None,
        "screening_in_progress": False,
        "call_transcript": None,
        "notice_period": None,
        "current_compensation": None,
        "expected_compensation": None,
        "created_by_id": ObjectId(created_by_id) if created_by_id else None,
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC)
    }

def serialize_user(user: dict) -> dict:
    """Convert MongoDB user document to JSON-serializable format"""
    return {
        "id": str(user["_id"]),
        "email": user["email"],
        "full_name": user["full_name"],
        "is_active": user["is_active"],
        "is_superuser": user["is_superuser"],
        "created_at": user["created_at"].isoformat(),
        "updated_at": user["updated_at"].isoformat()
    }

def serialize_job(job: dict) -> dict:
    """Convert MongoDB job document to JSON-serializable format matching frontend expectations"""
    return {
        "id": str(job["_id"]) if isinstance(job["_id"], ObjectId) else str(job["_id"]),
        "title": job["title"],
        "description": job["description"],
        "responsibilities": job["responsibilities"],
        "requirements": job["requirements"],
        "total_candidates": int(job.get("total_candidates", 0)),
        "resume_screened": int(job.get("resume_screened", 0)),
        "phone_screened": int(job.get("phone_screened", 0)),
        "created_by_id": str(job["created_by_id"]) if isinstance(job["created_by_id"], ObjectId) else str(job["created_by_id"]),
        "created_at": job["created_at"].isoformat() if isinstance(job["created_at"], datetime) else job["created_at"],
        "updated_at": job["updated_at"].isoformat() if isinstance(job["updated_at"], datetime) else job["updated_at"]
    }

def serialize_candidate(candidate: dict) -> dict:
    """Convert MongoDB candidate document to JSON-serializable format"""
    try:
        # Get either resume_file_id or resume_path
        resume_identifier = candidate.get("resume_file_id", candidate.get("resume_path", ""))
        
        return {
            "id": str(candidate["_id"]),
            "job_id": str(candidate["job_id"]),
            "name": candidate["name"],
            "email": candidate["email"],
            "phone": candidate["phone"],
            "location": candidate["location"],
            "resume_file_id": resume_identifier,  # Use whichever we found
            "skills": candidate["skills"],
            "resume_score": candidate["resume_score"],
            "screening_score": candidate["screening_score"],
            "screening_summary": candidate["screening_summary"],
            "screening_in_progress": candidate.get("screening_in_progress", False),
            "call_transcript": candidate.get("call_transcript"),
            "notice_period": candidate.get("notice_period"),
            "current_compensation": candidate.get("current_compensation"),
            "expected_compensation": candidate.get("expected_compensation"),
            "created_by_id": str(candidate["created_by_id"]) if candidate.get("created_by_id") else None,
            "created_at": candidate["created_at"].isoformat(),
            "updated_at": candidate["updated_at"].isoformat()
        }
    except Exception as e:
        logger.error(f"Error serializing candidate {candidate.get('_id', 'unknown')}: {str(e)}")
        logger.error(f"Candidate data: {candidate}")
        raise

async def get_candidate_by_id(candidate_id: str) -> Optional[dict]:
    """
    Get a candidate by ID without requiring the job_id
    """
    from app.core.mongodb import get_database
    
    try:
        db = await get_database()
        candidate_data = await db.candidates.find_one({"_id": ObjectId(candidate_id)})
        if candidate_data:
            return serialize_candidate(candidate_data)
        return None
    except Exception as e:
        logger.error(f"Error fetching candidate by ID: {str(e)}", exc_info=True)
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=f"Error fetching candidate: {str(e)}") 