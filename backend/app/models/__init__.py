# backend/app/models/__init__.py
"""
Additional database models for the Purretys application
This file contains: Item, Inventory, Transaction, Message, Notification, Achievement models
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Enum, JSON, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from datetime import datetime

from app.core.database import Base


# ==================== Items & Inventory ====================

class ItemType(enum.Enum):
    """Item type enumeration"""
    FOOD = "food"
    TOY = "toy"
    ACCESSORY = "accessory"
    MEDICINE = "medicine"
    SPECIAL = "special"


class Item(Base):
    """
    Items that can be purchased and used in the game
    """
    __tablename__ = "items"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Item information
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    item_type = Column(Enum(ItemType), nullable=False, index=True)
    
    # Cost and availability
    cost = Column(Integer, nullable=False)
    is_available = Column(Boolean, default=True, nullable=False)
    unlock_level = Column(Integer, default=1, nullable=False)  # Required pet level
    
    # Effects (JSON object with metric changes)
    effects = Column(JSON, nullable=False)  # e.g., {"happiness": 20, "hunger": -30}
    duration = Column(Integer, default=0, nullable=False)  # Effect duration in minutes (0 = instant)
    
    # Visual
    icon_url = Column(String(500), nullable=True)
    
    # Special properties
    is_consumable = Column(Boolean, default=True, nullable=False)
    max_stack = Column(Integer, default=99, nullable=False)
    cooldown = Column(Integer, default=0, nullable=False)  # Cooldown in minutes
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    inventory_items = relationship("Inventory", back_populates="item")


class Inventory(Base):
    """
    Pet inventory for storing items
    """
    __tablename__ = "inventory"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Foreign keys
    pet_id = Column(Integer, ForeignKey("pets.id"), nullable=False, index=True)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False)
    
    # Quantity
    quantity = Column(Integer, default=1, nullable=False)
    
    # Usage tracking
    last_used_at = Column(DateTime(timezone=True), nullable=True)
    total_used = Column(Integer, default=0, nullable=False)
    
    # Timestamps
    acquired_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    pet = relationship("Pet", back_populates="inventory")
    item = relationship("Item", back_populates="inventory_items")


# ==================== Transactions ====================

class TransactionType(enum.Enum):
    """Transaction type enumeration"""
    TASK_REWARD = "task_reward"
    ITEM_PURCHASE = "item_purchase"
    MINI_GAME_REWARD = "mini_game_reward"
    DAILY_BONUS = "daily_bonus"
    ACHIEVEMENT_REWARD = "achievement_reward"
    GIFT = "gift"
    OTHER = "other"


class Transaction(Base):
    """
    Currency transaction history
    """
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Foreign keys
    pet_id = Column(Integer, ForeignKey("pets.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Transaction details
    amount = Column(Integer, nullable=False)  # Positive for earning, negative for spending
    transaction_type = Column(Enum(TransactionType), nullable=False, index=True)
    description = Column(String(255), nullable=False)
    
    # Related entities (optional)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=True)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=True)
    
    # Balance after transaction
    balance_after = Column(Integer, nullable=False)
    
    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    # Relationships
    pet = relationship("Pet", back_populates="transactions")
    user = relationship("User", back_populates="transactions")


# ==================== Communication ====================

class Message(Base):
    """
    In-app messages between pet co-owners
    """
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Foreign keys
    pet_id = Column(Integer, ForeignKey("pets.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Message content
    content = Column(Text, nullable=False)
    
    # Mentions
    mentioned_users = Column(JSON, nullable=True)  # Array of user_ids mentioned
    
    # Status
    is_edited = Column(Boolean, default=False, nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    
    # Read receipts (JSON array of {user_id, read_at})
    read_receipts = Column(JSON, nullable=True)
    
    # Relationships
    pet = relationship("Pet", back_populates="messages")
    user = relationship("User", back_populates="messages")


class NotificationType(enum.Enum):
    """Notification type enumeration"""
    PET_HUNGRY = "pet_hungry"
    PET_SAD = "pet_sad"
    PET_SICK = "pet_sick"
    TASK_ASSIGNED = "task_assigned"
    TASK_COMPLETED = "task_completed"
    TASK_REMINDER = "task_reminder"
    CURRENCY_EARNED = "currency_earned"
    ACHIEVEMENT_UNLOCKED = "achievement_unlocked"
    INVITE_RECEIVED = "invite_received"
    MENTION = "mention"
    SYSTEM = "system"


class Notification(Base):
    """
    User notifications
    """
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    pet_id = Column(Integer, ForeignKey("pets.id"), nullable=True)
    
    # Notification details
    notification_type = Column(Enum(NotificationType), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    
    # Priority
    priority = Column(String(20), default="normal", nullable=False)  # low, normal, high, critical
    
    # Status
    is_read = Column(Boolean, default=False, nullable=False, index=True)
    read_at = Column(DateTime(timezone=True), nullable=True)
    
    # Action URL (for navigation)
    action_url = Column(String(255), nullable=True)
    
    # Additional data
    data = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # Push notification status
    push_sent = Column(Boolean, default=False, nullable=False)
    push_sent_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="notifications")


# ==================== Achievements ====================

class AchievementCategory(enum.Enum):
    """Achievement category enumeration"""
    CARE = "care"
    TASKS = "tasks"
    SOCIAL = "social"
    COLLECTION = "collection"
    MILESTONES = "milestones"
    SPECIAL = "special"


class Achievement(Base):
    """
    Achievement definitions
    """
    __tablename__ = "achievements"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Achievement information
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=False)
    category = Column(Enum(AchievementCategory), nullable=False, index=True)
    
    # Requirements (JSON object with conditions)
    requirements = Column(JSON, nullable=False)  # e.g., {"tasks_completed": 100}
    
    # Rewards
    currency_reward = Column(Integer, default=0, nullable=False)
    experience_reward = Column(Integer, default=0, nullable=False)
    item_reward_id = Column(Integer, ForeignKey("items.id"), nullable=True)
    
    # Visual
    icon_url = Column(String(500), nullable=True)
    badge_color = Column(String(20), default="bronze", nullable=False)
    
    # Rarity
    rarity = Column(String(20), default="common", nullable=False)  # common, rare, epic, legendary
    points = Column(Integer, default=10, nullable=False)  # Achievement points
    
    # Availability
    is_active = Column(Boolean, default=True, nullable=False)
    is_secret = Column(Boolean, default=False, nullable=False)
    
    # Order
    display_order = Column(Integer, default=0, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    user_achievements = relationship("UserAchievement", back_populates="achievement")


class UserAchievement(Base):
    """
    User achievement progress and unlocks
    """
    __tablename__ = "user_achievements"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    achievement_id = Column(Integer, ForeignKey("achievements.id"), nullable=False, index=True)
    pet_id = Column(Integer, ForeignKey("pets.id"), nullable=True)  # Associated pet if applicable
    
    # Progress
    progress = Column(JSON, nullable=True)  # JSON object tracking progress
    progress_percentage = Column(Float, default=0.0, nullable=False)
    
    # Unlock status
    is_unlocked = Column(Boolean, default=False, nullable=False, index=True)
    unlocked_at = Column(DateTime(timezone=True), nullable=True)
    
    # Notification sent
    notification_sent = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    started_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="achievements")
    achievement = relationship("Achievement", back_populates="user_achievements")


# ==================== Pet Invitations ====================

class InvitationStatus(enum.Enum):
    """Invitation status enumeration"""
    PENDING = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class PetInvitation(Base):
    """
    Pet co-ownership invitations
    """
    __tablename__ = "pet_invitations"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Foreign keys
    pet_id = Column(Integer, ForeignKey("pets.id"), nullable=False, index=True)
    inviter_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    invitee_email = Column(String(255), nullable=False, index=True)
    invitee_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Set when user found
    
    # Invitation details
    role = Column(String(20), default="co-owner", nullable=False)
    message = Column(Text, nullable=True)
    
    # Status
    status = Column(Enum(InvitationStatus), default=InvitationStatus.PENDING, nullable=False, index=True)
    
    # Invitation token (for email invites)
    invitation_token = Column(String(255), unique=True, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    responded_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    inviter = relationship("User", foreign_keys=[inviter_id])
    invitee = relationship("User", foreign_keys=[invitee_id])


# ==================== Export all models ====================

# Import models from other files for centralized access
from app.models.user import User
from app.models.pet import (
    Pet, PetOwnership, PetMetrics, PetMetricsHistory, 
    PetActivityLog, PetState, PetStage
)
from app.models.task import (
    Task, TaskAssignment, TaskCompletion, TaskComment,
    TaskCategory, TaskDifficulty, TaskStatus, RecurrencePattern
)

__all__ = [
    # User models
    "User",
    
    # Pet models
    "Pet",
    "PetOwnership",
    "PetMetrics",
    "PetMetricsHistory",
    "PetActivityLog",
    "PetState",
    "PetStage",
    
    # Task models
    "Task",
    "TaskAssignment",
    "TaskCompletion",
    "TaskComment",
    "TaskCategory",
    "TaskDifficulty",
    "TaskStatus",
    "RecurrencePattern",
    
    # Item and inventory
    "Item",
    "Inventory",
    "ItemType",
    
    # Transactions
    "Transaction",
    "TransactionType",
    
    # Communication
    "Message",
    "Notification",
    "NotificationType",
    
    # Achievements
    "Achievement",
    "UserAchievement",
    "AchievementCategory",
    
    # Invitations
    "PetInvitation",
    "InvitationStatus"
]