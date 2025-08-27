# backend/app/core/security.py
"""
Security utilities for password hashing and JWT token management
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
import secrets
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token
    
    Args:
        data: Data to encode in the token
        expires_delta: Optional custom expiration time
    
    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    })
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    
    return encoded_jwt

def create_refresh_token(data: Dict[str, Any]) -> str:
    """
    Create a JWT refresh token
    
    Args:
        data: Data to encode in the token
    
    Returns:
        Encoded refresh token
    """
    to_encode = data.copy()
    
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh",
        "jti": secrets.token_urlsafe(32)  # Unique token ID for blacklisting
    })
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    
    return encoded_jwt

def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Decode and validate a JWT token
    
    Args:
        token: The JWT token to decode
    
    Returns:
        Decoded token payload or None if invalid
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError as e:
        logger.error(f"JWT decode error: {e}")
        return None
    except Exception as e:
        logger.error(f"Token decode error: {e}")
        return None

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password
    
    Args:
        plain_password: The plain text password
        hashed_password: The hashed password to compare against
    
    Returns:
        True if passwords match, False otherwise
    """
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        logger.error(f"Password verification error: {e}")
        return False

def get_password_hash(password: str) -> str:
    """
    Hash a password
    
    Args:
        password: The plain text password to hash
    
    Returns:
        Hashed password
    """
    return pwd_context.hash(password)

def generate_password_reset_token(email: str) -> str:
    """
    Generate a password reset token
    
    Args:
        email: User's email address
    
    Returns:
        Password reset token
    """
    data = {
        "sub": email,
        "type": "password_reset"
    }
    
    expire = datetime.utcnow() + timedelta(hours=24)  # 24 hour expiration
    data.update({"exp": expire})
    
    return jwt.encode(
        data,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

def verify_password_reset_token(token: str) -> Optional[str]:
    """
    Verify a password reset token
    
    Args:
        token: The reset token to verify
    
    Returns:
        Email address if valid, None otherwise
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        
        if payload.get("type") != "password_reset":
            return None
        
        return payload.get("sub")
    except JWTError:
        return None

def generate_email_verification_token(email: str) -> str:
    """
    Generate an email verification token
    
    Args:
        email: User's email address
    
    Returns:
        Email verification token
    """
    data = {
        "sub": email,
        "type": "email_verification"
    }
    
    expire = datetime.utcnow() + timedelta(days=7)  # 7 day expiration
    data.update({"exp": expire})
    
    return jwt.encode(
        data,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

def verify_email_verification_token(token: str) -> Optional[str]:
    """
    Verify an email verification token
    
    Args:
        token: The verification token
    
    Returns:
        Email address if valid, None otherwise
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        
        if payload.get("type") != "email_verification":
            return None
        
        return payload.get("sub")
    except JWTError:
        return None

def generate_api_key() -> str:
    """
    Generate a secure API key
    
    Returns:
        A secure random API key
    """
    return secrets.token_urlsafe(32)

def hash_api_key(api_key: str) -> str:
    """
    Hash an API key for storage
    
    Args:
        api_key: The API key to hash
    
    Returns:
        Hashed API key
    """
    # Use a different context for API keys (faster, since they're random)
    return pwd_context.hash(api_key)

def verify_api_key(api_key: str, hashed_key: str) -> bool:
    """
    Verify an API key
    
    Args:
        api_key: The plain API key
        hashed_key: The hashed API key to compare against
    
    Returns:
        True if keys match, False otherwise
    """
    try:
        return pwd_context.verify(api_key, hashed_key)
    except Exception:
        return False