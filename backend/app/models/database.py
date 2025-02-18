from datetime import datetime
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
        self.created_at = data.get("created_at", datetime.utcnow())
        self.updated_at = data.get("updated_at", datetime.utcnow())

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
        self.created_by_id = str(data.get("created_by_id")) if data.get("created_by_id") else None
        self.created_at = data.get("created_at", datetime.utcnow())
        self.updated_at = data.get("updated_at", datetime.utcnow())

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
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
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
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
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
        "id": str(ObjectId()),  # Add string ID for frontend
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
        "created_by_id": ObjectId(created_by_id) if created_by_id else None,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
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
        "id": str(job["_id"]),
        "title": job["title"],
        "description": job["description"],
        "responsibilities": job["responsibilities"],
        "requirements": job["requirements"],
        "total_candidates": int(job.get("total_candidates", 0)),
        "resume_screened": int(job.get("resume_screened", 0)),
        "phone_screened": int(job.get("phone_screened", 0)),
        "created_by_id": str(job["created_by_id"]),
        "created_at": job["created_at"].isoformat(),
        "updated_at": job["updated_at"].isoformat()
    }

def serialize_candidate(candidate: dict) -> dict:
    """Convert MongoDB candidate document to JSON-serializable format"""
    return {
        "id": str(candidate["_id"]),
        "job_id": str(candidate["job_id"]),
        "name": candidate["name"],
        "email": candidate["email"],
        "phone": candidate["phone"],
        "location": candidate["location"],
        "resume_file_id": candidate["resume_file_id"],
        "skills": candidate["skills"],
        "resume_score": candidate["resume_score"],
        "screening_score": candidate["screening_score"],
        "screening_summary": candidate["screening_summary"],
        "created_by_id": str(candidate["created_by_id"]) if candidate["created_by_id"] else None,
        "created_at": candidate["created_at"].isoformat(),
        "updated_at": candidate["updated_at"].isoformat()
    } 