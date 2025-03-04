import pytest
import asyncio
import os
import sys
from unittest.mock import patch, AsyncMock, MagicMock
from bson import ObjectId
from datetime import datetime, timedelta
from fastapi import HTTPException

# Add parent directory to path to allow imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from app.services.auth import (
    authenticate_user,
    create_access_token,
    get_current_user,
    get_current_active_user,
    get_user_by_email,
    create_user
)

@pytest.mark.asyncio
async def test_get_user_by_email(mock_get_database, mock_user):
    """Test getting a user by email"""
    email = mock_user["email"]
    
    # Call the get_user_by_email function
    result = await get_user_by_email(email)
    
    # Verify the result
    assert result is not None
    assert result["email"] == email
    
    # Verify the database was called correctly
    mock_db = mock_get_database
    mock_db.users.find_one.assert_called_once()

@pytest.mark.asyncio
async def test_get_user_by_email_not_found(mock_get_database):
    """Test getting a user that doesn't exist"""
    # Setup the mock to return None
    mock_db = mock_get_database
    mock_db.users.find_one.return_value = None
    
    # Call the get_user_by_email function with a non-existent email
    result = await get_user_by_email("nonexistent@example.com")
    
    # Verify the result is None
    assert result is None

@pytest.mark.asyncio
async def test_authenticate_user_success(mock_get_database, mock_user, mock_password_context):
    """Test successful user authentication"""
    email = mock_user["email"]
    password = "testpassword123"
    
    # Call the authenticate_user function
    result = await authenticate_user(email, password)
    
    # Verify the result
    assert result is not None
    assert result["email"] == email
    
    # Verify the password was verified
    mock_password_context.verify.assert_called_once_with(password, mock_user["hashed_password"])

@pytest.mark.asyncio
async def test_authenticate_user_wrong_password(mock_get_database, mock_user, mock_password_context):
    """Test authentication with wrong password"""
    email = mock_user["email"]
    password = "wrongpassword"
    
    # Setup the mock to return False for password verification
    mock_password_context.verify.return_value = False
    
    # Call the authenticate_user function
    result = await authenticate_user(email, password)
    
    # Verify the result is None
    assert result is None
    
    # Verify the password was verified
    mock_password_context.verify.assert_called_once_with(password, mock_user["hashed_password"])

@pytest.mark.asyncio
async def test_authenticate_user_not_found(mock_get_database):
    """Test authentication with non-existent user"""
    # Setup the mock to return None
    mock_db = mock_get_database
    mock_db.users.find_one.return_value = None
    
    # Call the authenticate_user function with a non-existent email
    result = await authenticate_user("nonexistent@example.com", "testpassword123")
    
    # Verify the result is None
    assert result is None

@pytest.mark.asyncio
async def test_create_access_token():
    """Test creating an access token"""
    data = {"sub": "test@example.com"}
    
    # Call the create_access_token function
    token = create_access_token(data)
    
    # Verify the token is a string
    assert isinstance(token, str)
    assert len(token) > 0

@pytest.mark.asyncio
async def test_get_current_user(mock_token):
    """Test getting the current user from a token"""
    # Mock the token verification
    with patch("app.services.auth.jwt.decode") as mock_decode, \
         patch("app.services.auth.get_database") as mock_get_database:
        
        # Create a valid ObjectId
        user_id = "507f1f77bcf86cd799439011"  # Valid 24-character hex string
        
        # Setup the mocks
        mock_decode.return_value = {"sub": user_id}
        
        # Mock the database and find_one method
        mock_db = AsyncMock()
        mock_get_database.return_value = mock_db
        mock_db.users = AsyncMock()
        mock_db.users.find_one.return_value = {
            "_id": user_id,
            "email": "test@example.com", 
            "is_active": True
        }
        
        # Call the get_current_user function
        result = await get_current_user(mock_token)
        
        # Verify the result
        assert result is not None
        assert result["email"] == "test@example.com"
        
        # Verify the token was decoded
        mock_decode.assert_called_once()
        mock_db.users.find_one.assert_called_once_with({"_id": ObjectId(user_id)})

@pytest.mark.asyncio
async def test_get_current_user_invalid_token():
    """Test getting the current user with an invalid token"""
    # Mock the token verification to raise an exception
    with patch("app.services.auth.jwt.decode") as mock_decode:
        mock_decode.side_effect = Exception("Invalid token")
        
        # Call the get_current_user function with an invalid token
        with pytest.raises(HTTPException) as excinfo:
            await get_current_user("invalid_token")
        
        # Verify the exception
        assert excinfo.value.status_code == 401
        assert "Could not validate credentials" in excinfo.value.detail

@pytest.mark.asyncio
async def test_get_current_active_user():
    """Test getting the current active user"""
    # Mock an active user
    mock_user = {"email": "test@example.com", "is_active": True}
    
    # Call the get_current_active_user function
    result = await get_current_active_user(mock_user)
    
    # Verify the result
    assert result is not None
    assert result["email"] == "test@example.com"

@pytest.mark.asyncio
async def test_get_current_active_user_inactive():
    """Test getting an inactive user"""
    # Mock an inactive user
    mock_user = {"email": "test@example.com", "is_active": False}
    
    # Call the get_current_active_user function with an inactive user
    with pytest.raises(HTTPException) as excinfo:
        await get_current_active_user(mock_user)
    
    # Verify the exception
    assert excinfo.value.status_code == 400
    assert "Inactive user" in excinfo.value.detail

@pytest.mark.asyncio
async def test_create_user(mock_get_database, mock_user_data, mock_password_context):
    """Test creating a new user"""
    # Call the create_user function
    result = await create_user(
        email=mock_user_data["email"],
        password=mock_user_data["password"],
        full_name=mock_user_data["full_name"]
    )
    
    # Verify the result
    assert result is not None
    assert result["email"] == mock_user_data["email"]
    assert result["full_name"] == mock_user_data["full_name"]
    
    # Verify the password was hashed
    mock_password_context.hash.assert_called_once_with(mock_user_data["password"])
    
    # Verify the database was called correctly
    mock_db = mock_get_database
    mock_db.users.insert_one.assert_called_once() 