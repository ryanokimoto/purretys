# backend/app/models/task.py
"""
Task model for real-world task management and gamification
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Enum, JSON, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from datetime import datetime

from app.core.database import Base


class TaskCategory(enum.Enum):
    """Task category enumeration"""
    EXERCISE = "exercise"
    HYDRATION = "hydration"
    STUDY = "study"
    CHORES = "chores"
    SOCIAL = "social"
    WORK = "work"
    SELF_CARE = "self_care"
    CUSTOM = "custom"


class TaskDifficulty(enum.Enum):
    """Task difficulty levels"""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    EXPERT = "expert"


class TaskStatus(enum.Enum):
    """Task status"""
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class RecurrencePattern(enum.Enum):
    """Task recurrence patterns"""
    NONE = "none"
    DAILY = "daily"
    WEEKLY = "weekly"
    BIWEEKLY = "biweekly"
    MONTHLY = "monthly"
    CUSTOM = "custom"


class Task(Base):
    """
    Task model for real-world tasks that earn currency
    """
    __tablename__ = "tasks"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Task information
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(Enum(TaskCategory), default=TaskCategory.CUSTOM, nullable=False, index=True)
    difficulty = Column(Enum(TaskDifficulty), default=TaskDifficulty.MEDIUM, nullable=False)
    status = Column(Enum(TaskStatus), default=TaskStatus.ACTIVE, nullable=False, index=True)
    
    # Associated pet and creator
    pet_id = Column(Integer, ForeignKey("pets.id"), nullable=False, index=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Rewards
    currency_reward = Column(Integer, default=10, nullable=False)
    experience_reward = Column(Integer, default=5, nullable=False)
    
    # Metric impacts (JSON object with metric changes)
    metric_impacts = Column(JSON, nullable=True)  # e.g., {"happiness": 5, "health": 10}
    
    # Recurrence
    recurring = Column(Boolean, default=False, nullable=False)
    recurrence_pattern = Column(Enum(RecurrencePattern), default=RecurrencePattern.NONE, nullable=False)
    recurrence_details = Column(JSON, nullable=True)  # Custom recurrence rules
    parent_task_id = Column(Integer, ForeignKey("tasks.id"), nullable=True)  # For recurring task instances
    
    # Timing
    due_date = Column(DateTime(timezone=True), nullable=True)
    reminder_time = Column(DateTime(timezone=True), nullable=True)
    estimated_duration = Column(Integer, nullable=True)  # In minutes
    
    # Verification
    requires_proof = Column(Boolean, default=False, nullable=False)
    proof_type = Column(String(50), nullable=True)  # photo, timer, location, etc.
    
    # Streak tracking
    streak_count = Column(Integer, default=0, nullable=False)
    max_streak = Column(Integer, default=0, nullable=False)
    last_completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Priority and tags
    priority = Column(Integer, default=0, nullable=False)  # Higher number = higher priority
    tags = Column(JSON, nullable=True)  # Array of tags
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    
    # Completion statistics
    total_completions = Column(Integer, default=0, nullable=False)
    completion_rate = Column(Float, default=0.0, nullable=False)  # Percentage
    
    # Relationships
    pet = relationship("Pet", back_populates="tasks")
    creator = relationship("User", back_populates="created_tasks", foreign_keys=[created_by])
    
    assignments = relationship(
        "TaskAssignment",
        back_populates="task",
        cascade="all, delete-orphan"
    )
    
    completions = relationship(
        "TaskCompletion",
        back_populates="task",
        cascade="all, delete-orphan",
        order_by="TaskCompletion.completed_at.desc()"
    )
    
    child_tasks = relationship(
        "Task",
        backref="parent_task",
        foreign_keys=[parent_task_id],
        remote_side=[id]
    )
    
    comments = relationship(
        "TaskComment",
        back_populates="task",
        cascade="all, delete-orphan",
        order_by="TaskComment.created_at.desc()"
    )
    
    def __repr__(self):
        return f"<Task(id={self.id}, title={self.title}, category={self.category})>"


class TaskAssignment(Base):
    """
    Task assignment to specific users
    """
    __tablename__ = "task_assignments"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Foreign keys
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    assigned_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Assignment details
    assigned_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    accepted = Column(Boolean, default=False, nullable=False)
    accepted_at = Column(DateTime(timezone=True), nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    task = relationship("Task", back_populates="assignments")
    user = relationship("User", back_populates="task_assignments", foreign_keys=[user_id])
    assigner = relationship("User", foreign_keys=[assigned_by])


class TaskCompletion(Base):
    """
    Task completion records
    """
    __tablename__ = "task_completions"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Foreign keys
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Completion details
    completed_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    time_taken = Column(Integer, nullable=True)  # In minutes
    
    # Proof/verification
    proof_url = Column(String(500), nullable=True)  # URL to uploaded proof (photo, etc.)
    proof_type = Column(String(50), nullable=True)
    verified = Column(Boolean, default=False, nullable=False)
    verified_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    verified_at = Column(DateTime(timezone=True), nullable=True)
    
    # Rewards given
    currency_earned = Column(Integer, nullable=False)
    experience_earned = Column(Integer, nullable=False)
    metrics_applied = Column(JSON, nullable=True)  # Actual metric changes applied
    
    # Notes
    notes = Column(Text, nullable=True)
    
    # Quality/rating (for future gamification)
    quality_score = Column(Integer, nullable=True)  # 1-5 rating
    
    # Relationships
    task = relationship("Task", back_populates="completions")
    user = relationship("User", back_populates="task_completions", foreign_keys=[user_id])
    verifier = relationship("User", foreign_keys=[verified_by])


class TaskComment(Base):
    """
    Comments on tasks for collaboration
    """
    __tablename__ = "task_comments"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Foreign keys
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    parent_comment_id = Column(Integer, ForeignKey("task_comments.id"), nullable=True)
    
    # Comment content
    content = Column(Text, nullable=False)
    
    # Mentions
    mentioned_users = Column(JSON, nullable=True)  # Array of user_ids mentioned
    
    # Status
    is_edited = Column(Boolean, default=False, nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    
    # Relationships
    task = relationship("Task", back_populates="comments")
    user = relationship("User", foreign_keys=[user_id])
    
    replies = relationship(
        "TaskComment",
        backref="parent_comment",
        foreign_keys=[parent_comment_id],
        remote_side=[id]
    )