from typing import Any, Dict, Optional, List
import os
import logging
from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import computed_field

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

class Settings(BaseSettings):
    model_config = {
        "case_sensitive": True,
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore"  # This allows extra fields in env files
    }

    # Application settings
    PROJECT_NAME: str = "Recruitment AI"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    
    # MongoDB settings
    MONGODB_USERNAME: str
    MONGODB_PASSWORD: str
    MONGODB_CLUSTER: str
    MONGODB_DB_NAME: str
    
    # JWT settings
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS settings
    BACKEND_CORS_ORIGINS: List[str]
    
    # File upload settings
    MAX_UPLOAD_SIZE: int = 50 * 1024 * 1024  # 50MB
    ALLOWED_EXTENSIONS: set[str] = {"pdf", "zip"}

    # AI API settings
    AI_API_KEY: str
    AI_BASE_URL: str

    @computed_field
    def MONGODB_URL(self) -> str:
        return f"mongodb+srv://{self.MONGODB_USERNAME}:{self.MONGODB_PASSWORD}@{self.MONGODB_CLUSTER}/?retryWrites=true&w=majority&appName=Cluster0"

settings = Settings() 