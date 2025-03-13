from fastapi import APIRouter, Depends, HTTPException, Body
from typing import List, Dict, Any

from app.api.deps import get_current_user
from app.models.database import User
from app.services.voice_agent import (
    get_global_voice_config,
    update_global_voice_config,
    get_job_voice_config,
    update_job_voice_config,
    get_available_voices,
    get_available_models
)

router = APIRouter()


@router.get("/global-config")
async def read_global_voice_config(current_user: User = Depends(get_current_user)):
    """Get global voice agent configuration"""
    return await get_global_voice_config()


@router.put("/global-config")
async def update_global_config(
    config_data: Dict[str, Any] = Body(...),
    current_user: User = Depends(get_current_user)
):
    """Update global voice agent configuration"""
    return await update_global_voice_config(config_data, current_user)


@router.get("/job-config/{job_id}")
async def read_job_voice_config(
    job_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get job-specific voice agent configuration"""
    return await get_job_voice_config(job_id)


@router.put("/job-config/{job_id}")
async def update_job_config(
    job_id: str,
    config_data: Dict[str, Any] = Body(...),
    current_user: User = Depends(get_current_user)
):
    """Update job-specific voice agent configuration"""
    return await update_job_voice_config(job_id, config_data, current_user)


@router.get("/voices")
async def read_available_voices(current_user: User = Depends(get_current_user)):
    """Get list of available voices"""
    return await get_available_voices()


@router.get("/models")
async def read_available_models(current_user: User = Depends(get_current_user)):
    """Get list of available models"""
    return await get_available_models() 