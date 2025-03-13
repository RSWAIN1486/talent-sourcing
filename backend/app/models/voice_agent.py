from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class VoiceModel(str, Enum):
    ULTRAVOX_70B = "fixie-ai/ultravox"
    ULTRAVOX_LITE = "fixie-ai/ultravox-lite"


class GlobalVoiceConfig(BaseModel):
    """Global voice agent configuration that applies to all jobs"""
    model: Optional[str] = Field(default=VoiceModel.ULTRAVOX_70B)  # Make model optional
    voice_id: str = Field(default="ebae2397-0ba1-4222-9d5b-5313ddeb04b5")  # Default voice
    temperature: float = Field(default=0.7, ge=0, le=1.0)
    base_system_prompt: str = Field(
        default="You are an AI voice assistant conducting a brief screening for a job. "
                "Be professional, friendly, and keep it concise. Listen to the candidate's "
                "answers and respond appropriately."
    )
    default_questions: List[str] = Field(
        default=[
            "What is your notice period?",
            "What is your current compensation?",
            "What are your salary expectations for this role?"
        ]
    )
    recording_enabled: bool = Field(default=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now())
    updated_at: datetime = Field(default_factory=lambda: datetime.now())
    created_by_id: Optional[str] = None


class JobVoiceConfig(BaseModel):
    """Job-specific voice agent configuration"""
    job_id: str
    custom_system_prompt: Optional[str] = None
    custom_questions: Optional[List[str]] = None
    use_global_config: bool = Field(default=True)
    model: Optional[VoiceModel] = None
    voice_id: Optional[str] = None
    temperature: Optional[float] = None
    recording_enabled: Optional[bool] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now())
    updated_at: datetime = Field(default_factory=lambda: datetime.now())
    created_by_id: Optional[str] = None


class VoiceInfo(BaseModel):
    """Information about available voices"""
    id: str
    name: str
    language: str
    gender: Optional[str] = None
    description: Optional[str] = None
    preview_url: Optional[str] = None 