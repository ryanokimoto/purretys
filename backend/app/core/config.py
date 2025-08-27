# backend/app/core/config.py

import os
from typing import Any, Dict, Optional, List, Union
from pydantic_settings import BaseSettings
from pydantic import field_validator, ConfigDict


class Settings(BaseSettings):
    """
    Application settings and configuration management.
    Uses environment variables with fallback to defaults.
    """
    
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )
    
    # Application
    APP_NAME: str = "Purretys"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"
    SECRET_KEY: str = "change-this-secret-key-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Database
    DATABASE_URL: str = "sqlite:///./purretys.db"  # Default to SQLite for development
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 40
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_PASSWORD: Optional[str] = None
    
    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"
    
    # CORS - Use Union[str, List[str]] to handle both string and list inputs
    CORS_ORIGINS: Union[str, List[str]] = "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173,http://127.0.0.1:3000"
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: Union[str, List[str]] = "*"
    CORS_ALLOW_HEADERS: Union[str, List[str]] = "*"
    
    # WebSocket
    WS_MESSAGE_QUEUE: str = "redis://localhost:6379/3"
    
    # File Upload
    MAX_UPLOAD_SIZE: int = 10485760  # 10MB in bytes
    ALLOWED_EXTENSIONS: Union[str, List[str]] = "jpg,jpeg,png,gif,webp"
    UPLOAD_DIR: str = "uploads"
    
    # Email (for future notifications)
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_FROM: str = "noreply@purretys.com"
    
    # External APIs
    OPENAI_API_KEY: Optional[str] = None
    STRIPE_API_KEY: Optional[str] = None
    
    # Monitoring
    SENTRY_DSN: Optional[str] = None
    LOG_LEVEL: str = "INFO"
    
    # Game Configuration
    METRIC_DECAY_RATE: float = 0.1  # Points per hour
    TASK_COMPLETION_BONUS: Dict[str, int] = {
        "easy": 5,
        "medium": 10,
        "hard": 20
    }
    PET_INITIAL_METRICS: Dict[str, int] = {
        "happiness": 50,
        "hunger": 50,
        "health": 100,
        "energy": 50,
        "currency": 100
    }
    
    @field_validator('CORS_ORIGINS', mode='before')
    @classmethod
    def parse_cors_origins(cls, v: Any) -> List[str]:
        """Parse CORS origins from environment variable"""
        if isinstance(v, str):
            if v == "*":
                return ["*"]
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        elif isinstance(v, list):
            return v
        return ["http://localhost:5173", "http://localhost:3000"]  # fallback
    
    @field_validator('CORS_ALLOW_METHODS', mode='before')
    @classmethod
    def parse_cors_methods(cls, v: Any) -> List[str]:
        """Parse CORS methods from environment variable"""
        if isinstance(v, str):
            if v == "*":
                return ["*"]
            return [method.strip() for method in v.split(",") if method.strip()]
        elif isinstance(v, list):
            return v
        return ["*"]  # fallback
    
    @field_validator('CORS_ALLOW_HEADERS', mode='before')
    @classmethod
    def parse_cors_headers(cls, v: Any) -> List[str]:
        """Parse CORS headers from environment variable"""
        if isinstance(v, str):
            if v == "*":
                return ["*"]
            return [header.strip() for header in v.split(",") if header.strip()]
        elif isinstance(v, list):
            return v
        return ["*"]  # fallback
    
    @field_validator('ALLOWED_EXTENSIONS', mode='before')
    @classmethod
    def parse_allowed_extensions(cls, v: Any) -> List[str]:
        """Parse allowed file extensions from environment variable"""
        if isinstance(v, str):
            return [ext.strip() for ext in v.split(",") if ext.strip()]
        elif isinstance(v, list):
            return v
        return ["jpg", "jpeg", "png", "gif", "webp"]  # fallback
    
    @property
    def database_url_sync(self) -> str:
        """Get synchronous database URL for migrations"""
        if self.DATABASE_URL.startswith("postgresql+asyncpg://"):
            return self.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")
        return self.DATABASE_URL
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.ENVIRONMENT.lower() == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment"""
        return self.ENVIRONMENT.lower() == "development"


# Create global settings instance with error handling
try:
    settings = Settings()
except Exception as e:
    print(f"Configuration error: {e}")
    print("Using fallback configuration for development...")
    # Fallback to minimal settings for development
    settings = Settings(
        APP_NAME="Purretys",
        DEBUG=True,
        SECRET_KEY="development-secret-key",
        DATABASE_URL="sqlite:///./purretys.db",
        CORS_ORIGINS="http://localhost:5173,http://localhost:3000",
        CORS_ALLOW_METHODS="*",
        CORS_ALLOW_HEADERS="*"
    )