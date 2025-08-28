# backend/app/models/pet.py
"""
Pet model and related tables for the virtual pet system
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey, Text, Enum, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from datetime import datetime

from app.core.database import Base


class PetState(enum.Enum):
    """Pet state enumeration"""
    HAPPY = "happy"
    SAD = "sad"
    SLEEPING = "sleeping"
    HUNGRY = "hungry"
    SICK = "sick"
    PLAYFUL = "playful"
    TIRED = "tired"
    NEUTRAL = "neutral"


class PetStage(enum.Enum):
    """Pet growth stages"""
    KITTEN = "kitten"
    YOUNG = "young"
    ADULT = "adult"
    SENIOR = "senior"


class Pet(Base):
    """
    Pet model representing virtual cats
    """
    __tablename__ = "pets"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Basic information
    name = Column(String(50), nullable=False)
    sprite_id = Column(Integer, default=1, nullable=False)  # Visual appearance ID
    color = Column(String(20), default="orange", nullable=False)  # Pet color customization
    
    # Growth and state
    stage = Column(Enum(PetStage), default=PetStage.KITTEN, nullable=False)
    current_state = Column(Enum(PetState), default=PetState.NEUTRAL, nullable=False)
    level = Column(Integer, default=1, nullable=False)
    experience_points = Column(Integer, default=0, nullable=False)
    
    # Creation info
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    
    # Pet status
    is_active = Column(Boolean, default=True, nullable=False)
    is_sleeping = Column(Boolean, default=False, nullable=False)
    last_fed_at = Column(DateTime(timezone=True), nullable=True)
    last_played_at = Column(DateTime(timezone=True), nullable=True)
    last_petted_at = Column(DateTime(timezone=True), nullable=True)
    
    # Customization
    accessories = Column(JSON, nullable=True)  # JSON array of equipped accessories
    
    # Relationships
    creator = relationship("User", back_populates="owned_pets", foreign_keys=[created_by])
    
    ownerships = relationship(
        "PetOwnership",
        back_populates="pet",
        cascade="all, delete-orphan"
    )
    
    metrics = relationship(
        "PetMetrics",
        back_populates="pet",
        uselist=False,  # One-to-one relationship
        cascade="all, delete-orphan"
    )
    
    metrics_history = relationship(
        "PetMetricsHistory",
        back_populates="pet",
        cascade="all, delete-orphan",
        order_by="PetMetricsHistory.timestamp.desc()"
    )
    
    tasks = relationship(
        "Task",
        back_populates="pet",
        cascade="all, delete-orphan"
    )
    
    inventory = relationship(
        "Inventory",
        back_populates="pet",
        cascade="all, delete-orphan"
    )
    
    transactions = relationship(
        "Transaction",
        back_populates="pet",
        cascade="all, delete-orphan"
    )
    
    messages = relationship(
        "Message",
        back_populates="pet",
        cascade="all, delete-orphan"
    )
    
    activity_logs = relationship(
        "PetActivityLog",
        back_populates="pet",
        cascade="all, delete-orphan",
        order_by="PetActivityLog.created_at.desc()"
    )
    
    def __repr__(self):
        return f"<Pet(id={self.id}, name={self.name}, stage={self.stage})>"


class PetOwnership(Base):
    """
    Pet ownership relationship (many-to-many between users and pets)
    """
    __tablename__ = "pet_ownerships"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Foreign keys
    pet_id = Column(Integer, ForeignKey("pets.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Ownership details
    role = Column(String(20), default="co-owner", nullable=False)  # owner, co-owner
    joined_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Permissions (for future granular control)
    can_feed = Column(Boolean, default=True, nullable=False)
    can_play = Column(Boolean, default=True, nullable=False)
    can_spend_currency = Column(Boolean, default=True, nullable=False)
    can_create_tasks = Column(Boolean, default=True, nullable=False)
    can_invite_others = Column(Boolean, default=False, nullable=False)
    
    # Care statistics
    total_feeds = Column(Integer, default=0, nullable=False)
    total_plays = Column(Integer, default=0, nullable=False)
    total_tasks_completed = Column(Integer, default=0, nullable=False)
    
    # Relationships
    pet = relationship("Pet", back_populates="ownerships")
    user = relationship("User", back_populates="pet_ownerships")


class PetMetrics(Base):
    """
    Current pet metrics (health, happiness, etc.)
    """
    __tablename__ = "pet_metrics"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    pet_id = Column(Integer, ForeignKey("pets.id"), unique=True, nullable=False)
    
    # Core metrics (0-100)
    happiness = Column(Float, default=50.0, nullable=False)
    hunger = Column(Float, default=50.0, nullable=False)  # 100 = very hungry, 0 = full
    health = Column(Float, default=100.0, nullable=False)
    energy = Column(Float, default=50.0, nullable=False)
    
    # Currency
    currency = Column(Integer, default=100, nullable=False)
    total_currency_earned = Column(Integer, default=100, nullable=False)
    total_currency_spent = Column(Integer, default=0, nullable=False)
    
    # Metric modifiers (buffs/debuffs)
    happiness_modifier = Column(Float, default=1.0, nullable=False)
    health_modifier = Column(Float, default=1.0, nullable=False)
    energy_modifier = Column(Float, default=1.0, nullable=False)
    
    # Timestamps
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    last_decay_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    pet = relationship("Pet", back_populates="metrics", uselist=False)
    
    def to_dict(self):
        """Convert metrics to dictionary"""
        return {
            "happiness": round(self.happiness, 1),
            "hunger": round(self.hunger, 1),
            "health": round(self.health, 1),
            "energy": round(self.energy, 1),
            "currency": self.currency
        }


class PetMetricsHistory(Base):
    """
    Historical pet metrics for tracking and analytics
    """
    __tablename__ = "pet_metrics_history"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    pet_id = Column(Integer, ForeignKey("pets.id"), nullable=False, index=True)
    
    # Snapshot of metrics
    happiness = Column(Float, nullable=False)
    hunger = Column(Float, nullable=False)
    health = Column(Float, nullable=False)
    energy = Column(Float, nullable=False)
    currency = Column(Integer, nullable=False)
    
    # Context
    event_type = Column(String(50), nullable=True)  # fed, played, task_completed, decay, etc.
    event_details = Column(Text, nullable=True)
    
    # Timestamp
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    # Relationships
    pet = relationship("Pet", back_populates="metrics_history")


class PetActivityLog(Base):
    """
    Log of all activities performed with/on the pet
    """
    __tablename__ = "pet_activity_logs"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    pet_id = Column(Integer, ForeignKey("pets.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Activity details
    activity_type = Column(String(50), nullable=False)  # fed, played, petted, task_completed, etc.
    activity_details = Column(JSON, nullable=True)  # Additional context as JSON
    
    # Impact on metrics
    metrics_change = Column(JSON, nullable=True)  # JSON object with metric changes
    
    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    # Relationships
    pet = relationship("Pet", back_populates="activity_logs")
    user = relationship("User", foreign_keys=[user_id])