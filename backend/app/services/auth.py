from datetime import datetime, timedelta
from typing import Optional, Any
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
import motor.motor_asyncio

from app.core.config import settings
from app.core.mongodb import get_database
from app.models.database import create_user, serialize_user
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)

# OAuth2 scheme with correct API path
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

async def get_user_by_email(email: str, db: motor.motor_asyncio.AsyncIOMotorDatabase = Depends(get_database)) -> Optional[dict]:
    try:
        return await db.users.find_one({"email": email})
    except Exception as e:
        logger.error(f"Error getting user by email: {str(e)}", exc_info=True)
        raise

async def authenticate_user(email: str, password: str, db: motor.motor_asyncio.AsyncIOMotorDatabase = Depends(get_database)) -> Optional[dict]:
    try:
        user = await get_user_by_email(email, db)
        if not user:
            return None
        if not verify_password(password, user["hashed_password"]):
            return None
        return user
    except Exception as e:
        logger.error(f"Error authenticating user: {str(e)}", exc_info=True)
        raise

def create_access_token(user_id: str, expires_delta: Optional[timedelta] = None) -> str:
    try:
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        
        to_encode = {"exp": expire, "sub": str(user_id)}
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt
    except Exception as e:
        logger.error(f"Error creating access token: {str(e)}", exc_info=True)
        raise

async def get_current_user(token: str = Depends(oauth2_scheme), db: motor.motor_asyncio.AsyncIOMotorDatabase = Depends(get_database)) -> dict:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        
        user = await db.users.find_one({"_id": ObjectId(user_id)})
        if user is None:
            raise credentials_exception
        return user
    except JWTError as e:
        logger.error(f"JWT error: {str(e)}", exc_info=True)
        raise credentials_exception
    except Exception as e:
        logger.error(f"Error getting current user: {str(e)}", exc_info=True)
        raise

async def get_current_active_user(current_user: dict = Depends(get_current_user)) -> dict:
    if not current_user.get("is_active", True):  # Default to True if not set
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

async def create_new_user(email: str, password: str, full_name: str, db: motor.motor_asyncio.AsyncIOMotorDatabase = Depends(get_database)) -> dict:
    try:
        hashed_password = get_password_hash(password)
        
        user_data = create_user(
            email=email,
            hashed_password=hashed_password,
            full_name=full_name
        )
        
        await db.users.insert_one(user_data)
        return serialize_user(user_data)
    except Exception as e:
        logger.error(f"Error creating new user: {str(e)}", exc_info=True)
        raise 