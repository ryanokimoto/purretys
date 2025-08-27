# backend/app/api/v1/endpoints/auth.py
"""
Authentication endpoints for user registration and login
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, Field
import logging

from app.core.config import settings
from app.core.database import get_db
from app.core.security import (
    create_access_token,
    create_refresh_token,
    verify_password,
    get_password_hash,
    decode_token
)

logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

# Pydantic models for request/response
class UserRegister(BaseModel):
    """User registration schema"""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "username": "catcarer123",
                "password": "securepassword123"
            }
        }

class UserLogin(BaseModel):
    """User login schema"""
    email: EmailStr
    password: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "securepassword123"
            }
        }

class Token(BaseModel):
    """Token response schema"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

class TokenRefresh(BaseModel):
    """Token refresh schema"""
    refresh_token: str

class UserResponse(BaseModel):
    """User response schema"""
    id: int
    email: str
    username: str
    created_at: datetime
    is_active: bool = True

# Endpoints
@router.post("/register", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegister,
    db: Session = Depends(get_db)
):
    """
    Register a new user
    
    Returns:
        User information and authentication tokens
    """
    try:
        # Check if user already exists
        # Note: You'll need to import and create the User model
        # from app.models.user import User
        
        # For now, we'll return a mock response
        # In production, you would:
        # 1. Check if email/username exists
        # 2. Hash the password
        # 3. Create user in database
        # 4. Generate tokens
        
        # Mock user creation
        hashed_password = get_password_hash(user_data.password)
        
        # Create mock user object
        user = {
            "id": 1,
            "email": user_data.email,
            "username": user_data.username,
            "created_at": datetime.utcnow()
        }
        
        # Generate tokens
        access_token = create_access_token(
            data={"sub": user_data.email, "user_id": user["id"]}
        )
        refresh_token = create_refresh_token(
            data={"sub": user_data.email, "user_id": user["id"]}
        )
        
        return {
            "user": user,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "message": "User registered successfully"
        }
        
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Registration failed"
        )

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Login with email and password
    
    Returns:
        Access and refresh tokens
    """
    try:
        # In production, you would:
        # 1. Query user from database
        # 2. Verify password
        # 3. Generate tokens
        
        # Mock authentication
        # Note: form_data.username contains the email in OAuth2 flow
        email = form_data.username
        password = form_data.password
        
        # Mock user validation
        if email != "user@example.com" or password != "password123":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Generate tokens
        access_token = create_access_token(
            data={"sub": email, "user_id": 1}
        )
        refresh_token = create_refresh_token(
            data={"sub": email, "user_id": 1}
        )
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )

@router.post("/refresh", response_model=Token)
async def refresh_token(
    token_data: TokenRefresh,
    db: Session = Depends(get_db)
):
    """
    Refresh access token using refresh token
    
    Returns:
        New access and refresh tokens
    """
    try:
        # Decode refresh token
        payload = decode_token(token_data.refresh_token)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Generate new tokens
        email = payload.get("sub")
        user_id = payload.get("user_id")
        
        access_token = create_access_token(
            data={"sub": email, "user_id": user_id}
        )
        new_refresh_token = create_refresh_token(
            data={"sub": email, "user_id": user_id}
        )
        
        return {
            "access_token": access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed"
        )

@router.post("/logout")
async def logout(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Logout user (invalidate token)
    
    In production, you would add the token to a blacklist
    """
    try:
        # In production:
        # 1. Decode token to get user info
        # 2. Add token to blacklist in Redis
        # 3. Clear any server-side sessions
        
        return {
            "message": "Logged out successfully"
        }
        
    except Exception as e:
        logger.error(f"Logout error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )

@router.get("/me", response_model=UserResponse)
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Get current user information
    
    Returns:
        Current user data
    """
    try:
        # Decode token
        payload = decode_token(token)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        # In production, query user from database
        # For now, return mock data
        return UserResponse(
            id=payload.get("user_id", 1),
            email=payload.get("sub", "user@example.com"),
            username="catcarer123",
            created_at=datetime.utcnow(),
            is_active=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get user error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user information"
        )

# Dependency to get current user
async def get_current_active_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Dependency to get the current active user
    Use this in other endpoints that require authentication
    """
    payload = decode_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # In production, query user from database and check if active
    user = {
        "id": payload.get("user_id"),
        "email": payload.get("sub"),
        "is_active": True
    }
    
    if not user["is_active"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    return user