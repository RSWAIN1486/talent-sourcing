from datetime import datetime
from typing import Optional, Dict
from pydantic import BaseModel, ConfigDict

class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class CandidateResponse(BaseModel):
    id: str
    job_id: str
    name: str
    email: str
    phone: Optional[str] = None
    location: Optional[str] = None
    resume_file_id: str
    skills: Dict[str, float]
    resume_score: float
    screening_score: Optional[float] = None
    screening_summary: Optional[str] = None
    created_by_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True) 