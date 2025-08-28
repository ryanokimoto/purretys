# backend/app/models/user.py
"""
User model for authentication and profile management
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

from app.core.database import Base


class User(Base):
    """
    User model representing app users
    """
    __tablename__ = "users"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Authentication fields
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    
    # Profile fields
    display_name = Column(String(100), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    bio = Column(Text, nullable=True)
    
    # Account status
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Email verification
    email_verified_at = Column(DateTime(timezone=True), nullable=True)
    email_verification_token = Column(String(255), nullable=True)
    
    # Password reset
    password_reset_token = Column(String(255), nullable=True)
    password_reset_expires = Column(DateTime(timezone=True), nullable=True)
    
    # API keys (for future use)
    api_key = Column(String(255), nullable=True, unique=True)
    api_key_created_at = Column(DateTime(timezone=True), nullable=True)
    
    # Notification preferences
    notification_preferences = Column(Text, nullable=True)  # JSON field for preferences
    push_token = Column(String(255), nullable=True)  # For mobile push notifications
    
    # Relationships
    owned_pets = relationship(
        "Pet",
        back_populates="creator",
        foreign_keys="Pet.created_by",
        cascade="all, delete-orphan"
    )
    
    pet_ownerships = relationship(
        "PetOwnership",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    created_tasks = relationship(
        "Task",
        back_populates="creator",
        foreign_keys="Task.created_by",
        cascade="all, delete-orphan"
    )
    
    task_assignments = relationship(
        "TaskAssignment",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    task_completions = relationship(
        "TaskCompletion",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    transactions = relationship(
        "Transaction",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    messages = relationship(
        "Message",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    notifications = relationship(
        "Notification",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    achievements = relationship(
        "UserAchievement",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, email={self.email})>"
    
    def to_dict(self):
        """Convert user to dictionary for API responses"""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "display_name": self.display_name,
            "avatar_url": self.avatar_url,
            "bio": self.bio,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None
        }