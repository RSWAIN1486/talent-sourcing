import pytest
import os
import sys
import asyncio
from datetime import datetime, timedelta
from bson import ObjectId
from unittest.mock import AsyncMock, MagicMock, patch
from dotenv import load_dotenv
from jose import jwt

# Add parent directory to path to allow imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

# Load environment variables from the root directory
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
dotenv_path = os.path.join(root_dir, ".env")
load_dotenv(dotenv_path)

# Import app modules
from app.core.config import settings

# Fixtures for testing

@pytest.fixture
def mock_user_data():
    """Create mock user data for testing"""
    return {
        "email": "test@example.com",
        "password": "testpassword123",
        "full_name": "Test User"
    }

@pytest.fixture
def mock_user():
    """Create a mock user for testing"""
    user_id = str(ObjectId())
    return {
        "_id": ObjectId(user_id),
        "id": user_id,
        "email": "test@example.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "testpassword123"
        "full_name": "Test User",
        "is_active": True,
        "is_superuser": False,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }

@pytest.fixture
def mock_token():
    """Create a mock JWT token for testing"""
    # Create a token that expires in 30 minutes
    expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode = {
        "sub": "test@example.com",
        "exp": expire
    }
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

@pytest.fixture
def mock_db(mock_user):
    """Create a mock database client for testing"""
    mock_database = AsyncMock()
    
    # Mock collections
    mock_database.users = AsyncMock()
    
    # Setup default return values
    mock_database.users.find_one.return_value = mock_user
    mock_database.users.insert_one.return_value = AsyncMock(inserted_id=mock_user["_id"])
    
    return mock_database

@pytest.fixture
def mock_get_database(mock_db):
    """Patch the get_database function to return our mock"""
    async def _get_database():
        return mock_db
    
    with patch("app.services.auth.get_database", _get_database):
        yield mock_db

@pytest.fixture
def mock_password_context():
    """Mock the password context for testing"""
    mock_context = MagicMock()
    mock_context.hash.return_value = "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW"
    mock_context.verify.return_value = True
    
    with patch("app.services.auth.pwd_context", mock_context):
        yield mock_context 