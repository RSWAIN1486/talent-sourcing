from datetime import timedelta
from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.core.config import settings
from app.services import auth
from app.models.database import serialize_user
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()) -> Dict[str, str]:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    try:
        user = await auth.authenticate_user(form_data.username, form_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = auth.create_access_token(
            str(user["_id"]), expires_delta=access_token_expires
        )
        return {
            "access_token": access_token,
            "token_type": "bearer",
        }
    except Exception as e:
        logger.error(f"Login error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )

@router.post("/register")
async def register(request: Dict[str, Any]) -> Dict[str, Any]:
    """
    Register a new user
    """
    if not all(k in request for k in ["email", "password", "full_name"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing required fields"
        )
        
    user = await auth.get_user_by_email(request["email"])
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    user = await auth.create_new_user(
        email=request["email"],
        password=request["password"],
        full_name=request["full_name"]
    )
    return user

@router.get("/me")
async def read_users_me(current_user: dict = Depends(auth.get_current_active_user)) -> Dict[str, Any]:
    """
    Get current user
    """
    return serialize_user(current_user) 