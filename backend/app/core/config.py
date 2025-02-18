from typing import Any, Dict, Optional, List
import os
import logging
import json
from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import computed_field, field_validator
from urllib.parse import quote_plus

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
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 3000  # Increased to 3000 minutes
    
    # CORS settings
    BACKEND_CORS_ORIGINS: List[str] = []
    
    # File upload settings
    MAX_UPLOAD_SIZE: int = 50 * 1024 * 1024  # 50MB
    ALLOWED_EXTENSIONS: set[str] = {"pdf", "zip"}

    # AI API settings
    AI_API_KEY: str
    AI_BASE_URL: str

    @computed_field
    def MONGODB_URL(self) -> str:
        # URL encode the username and password
        username = quote_plus(self.MONGODB_USERNAME)
        password = quote_plus(self.MONGODB_PASSWORD)
        return f"mongodb+srv://{username}:{password}@{self.MONGODB_CLUSTER}/?retryWrites=true&w=majority&appName=Cluster0"

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v: str | List[str]) -> List[str]:
        if isinstance(v, str):
            try:
                # Try to parse as JSON first
                return json.loads(v)
            except json.JSONDecodeError:
                # If not JSON, split by comma
                return [i.strip() for i in v.split(",")]
        return v

settings = Settings() 