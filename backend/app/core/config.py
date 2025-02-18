from typing import Any, Dict, Optional, List
import os
import logging
from pathlib import Path
from pydantic_settings import BaseSettings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

class Settings(BaseSettings):
    PROJECT_NAME: str = "Recruitment AI"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    
    # MongoDB settings
    MONGODB_USERNAME: str = "your-username"
    MONGODB_PASSWORD: str = "your-password"
    MONGODB_CLUSTER: str = "your-cluster"
    MONGODB_URL: str
    MONGODB_DB_NAME: str = "recruitment_ai"
    
    # JWT settings
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS settings
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000"
    ]
    
    # OpenAI settings
    OPENAI_API_KEY: Optional[str] = None

    # File upload settings
    MAX_UPLOAD_SIZE: int = 50 * 1024 * 1024  # 50MB
    ALLOWED_EXTENSIONS: set[str] = {"pdf", "zip"}

    # AI API settings
    AI_API_KEY: str = "your-ai-api-key-here"
    AI_BASE_URL: str = "https://api.deepinfra.com/v1/openai"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Format MongoDB URL with credentials
        if not self.MONGODB_URL.startswith("mongodb+srv://your-username:"):  # Only format if not already formatted
            self.MONGODB_URL = self.MONGODB_URL.format(
                username=self.MONGODB_USERNAME,
                password=self.MONGODB_PASSWORD,
                cluster=self.MONGODB_CLUSTER
            )

    class Config:
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = 'utf-8'

settings = Settings() 