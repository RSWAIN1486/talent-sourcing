from fastapi import HTTPException
import httpx
from datetime import datetime
from typing import List, Optional, Dict, Any
from bson import ObjectId
from datetime import timezone

from app.core.config import settings
from app.core.logging import get_logger
from app.core.mongodb import get_database
from app.models.voice_agent import GlobalVoiceConfig, JobVoiceConfig, VoiceInfo, VoiceModel
from app.models.database import User

logger = get_logger(__name__)
UTC = timezone.utc


async def get_global_voice_config() -> GlobalVoiceConfig:
    """Get the global voice agent configuration"""
    db = await get_database()
    config = await db.voice_configs.find_one({"type": "global"})
    
    if not config:
        # Create default config if none exists
        default_config = GlobalVoiceConfig()
        config_dict = default_config.dict()
        config_dict["type"] = "global"
        
        result = await db.voice_configs.insert_one(config_dict)
        config = await db.voice_configs.find_one({"_id": result.inserted_id})
    
    # Convert ObjectId to string
    config["_id"] = str(config["_id"])
    
    # Ensure model is set
    if config.get('model') is None:
        config['model'] = VoiceModel.ULTRAVOX_70B
    
    return GlobalVoiceConfig(**config)


async def update_global_voice_config(config_data: Dict[str, Any], current_user: User) -> GlobalVoiceConfig:
    """Update the global voice agent configuration"""
    db = await get_database()
    
    # Get existing config
    existing_config = await db.voice_configs.find_one({"type": "global"})
    
    # Set default model if not provided or null
    if config_data.get('model') is None:
        config_data['model'] = VoiceModel.ULTRAVOX_70B
    
    if not existing_config:
        # Create new config if none exists
        config_data["type"] = "global"
        config_data["created_by_id"] = str(current_user.id)
        config_data["created_at"] = datetime.now(UTC)
        config_data["updated_at"] = datetime.now(UTC)
        
        result = await db.voice_configs.insert_one(config_data)
        updated_config = await db.voice_configs.find_one({"_id": result.inserted_id})
    else:
        # Update existing config
        config_data["updated_at"] = datetime.now(UTC)
        
        await db.voice_configs.update_one(
            {"_id": existing_config["_id"]},
            {"$set": config_data}
        )
        
        updated_config = await db.voice_configs.find_one({"_id": existing_config["_id"]})
    
    # Convert ObjectId to string
    updated_config["_id"] = str(updated_config["_id"])
    
    return GlobalVoiceConfig(**updated_config)


async def get_job_voice_config(job_id: str) -> JobVoiceConfig:
    """Get the voice agent configuration for a specific job"""
    db = await get_database()
    
    # Check if job exists
    job = await db.jobs.find_one({"_id": ObjectId(job_id)})
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Get job-specific config
    config = await db.voice_configs.find_one({"job_id": job_id, "type": "job"})
    
    if not config:
        # Create default job config if none exists
        default_config = JobVoiceConfig(job_id=job_id)
        config_dict = default_config.dict()
        config_dict["type"] = "job"
        
        result = await db.voice_configs.insert_one(config_dict)
        config = await db.voice_configs.find_one({"_id": result.inserted_id})
    
    # Convert ObjectId to string
    config["_id"] = str(config["_id"])
    
    return JobVoiceConfig(**config)


async def update_job_voice_config(job_id: str, config_data: Dict[str, Any], current_user: User) -> JobVoiceConfig:
    """Update the voice agent configuration for a specific job"""
    db = await get_database()
    
    # Check if job exists
    job = await db.jobs.find_one({"_id": ObjectId(job_id)})
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Get existing config
    existing_config = await db.voice_configs.find_one({"job_id": job_id, "type": "job"})
    
    if not existing_config:
        # Create new config if none exists
        config_data["job_id"] = job_id
        config_data["type"] = "job"
        config_data["created_by_id"] = str(current_user.id)
        config_data["created_at"] = datetime.now(UTC)
        config_data["updated_at"] = datetime.now(UTC)
        
        result = await db.voice_configs.insert_one(config_data)
        updated_config = await db.voice_configs.find_one({"_id": result.inserted_id})
    else:
        # Update existing config
        config_data["updated_at"] = datetime.now(UTC)
        
        await db.voice_configs.update_one(
            {"_id": existing_config["_id"]},
            {"$set": config_data}
        )
        
        updated_config = await db.voice_configs.find_one({"_id": existing_config["_id"]})
    
    # Convert ObjectId to string
    updated_config["_id"] = str(updated_config["_id"])
    
    return JobVoiceConfig(**updated_config)


async def get_available_voices() -> list[VoiceInfo]:
    """
    Retrieves available voices from the external API and transforms them into VoiceInfo objects.

    The external API returns data using pagination with voice records under the "results" key.

    Returns:
        A list of VoiceInfo objects.
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f'{settings.ULTRAVOX_API_BASE_URL}/api/voices',
            headers={
                'X-API-Key': settings.ULTRAVOX_API_KEY,
                'Content-Type': 'application/json'
            },
            timeout=30.0
        )
    
    response.raise_for_status()
    voices_data = response.json()
    # Debug log: remove or replace with proper logging when no longer needed.
    print(voices_data)

    voices = []
    # Use the "results" key since the API returns a paginated response.
    for voice in voices_data.get('results', []):
        voices.append(
            VoiceInfo(
                id=voice.get('voiceId'),
                name=voice.get('name'),
                language=voice.get('language') or '',
                gender=voice.get('gender', None),
                description=voice.get('description', None),
                preview_url=voice.get('previewUrl', None)
            )
        )
    return voices


async def get_available_models() -> list[dict]:
    """
    Retrieves available voice models from the external API and transforms them for frontend consumption.

    The external API returns models in a paginated format with records under the "results" key.

    Returns:
        A list of dictionaries containing model information.
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f'{settings.ULTRAVOX_API_BASE_URL}/api/models',
            headers={
                'X-API-Key': settings.ULTRAVOX_API_KEY,
                'Content-Type': 'application/json'
            },
            timeout=30.0
        )
    
    response.raise_for_status()
    models_data = response.json()
    # Debug log: remove or replace with proper logging when no longer needed.
    print(models_data)

    models = []
    # Transform records from the "results" key.
    for model in models_data.get('results', []):
        models.append({
            'id': model.get('id'),
            'name': model.get('name', model.get('id')),
            'description': model.get('description', '')
        })
    
    return models 