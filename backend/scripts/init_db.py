# backend/scripts/init_db.py
"""
Database initialization script
Run this to set up your database with tables and initial data
"""

import sys
import os
from pathlib import Path
import asyncio
from contextlib import asynccontextmanager

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text
from app.core.database import Base, engine, SessionLocal, init_db
from app.core.config import settings
from app.core.security import get_password_hash
import logging

# Import all models
from app.models.user import User
from app.models.pet import Pet, PetOwnership, PetMetrics, PetMetricsHistory, PetActivityLog
from app.models.task import Task, TaskAssignment, TaskCompletion, TaskComment
from app.models import (
    Item, Inventory, Transaction, Message, Notification,
    Achievement, UserAchievement, PetInvitation
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_tables():
    """Create all database tables"""
    logger.info("Creating database tables...")
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created successfully!")
    except Exception as e:
        logger.error(f"❌ Error creating tables: {e}")
        raise


def drop_tables():
    """Drop all database tables (USE WITH CAUTION!)"""
    logger.warning("Dropping all database tables...")
    try:
        Base.metadata.drop_all(bind=engine)
        logger.info("✅ All tables dropped successfully!")
    except Exception as e:
        logger.error(f"❌ Error dropping tables: {e}")
        raise


def create_initial_items():
    """Create initial items in the database"""
    db = SessionLocal()
    try:
        # Check if items already exist
        existing_items = db.query(Item).first()
        if existing_items:
            logger.info("Items already exist, skipping...")
            return
        
        initial_items = [
            {
                "name": "Catnip",
                "description": "A classic treat that makes your cat happy",
                "item_type": "food",
                "cost": 10,
                "effects": {"happiness": 20, "hunger": -30, "energy": 10},
                "icon_url": "/items/catnip.png"
            },
            {
                "name": "Tuna Treat",
                "description": "Delicious tuna that satisfies hunger",
                "item_type": "food",
                "cost": 15,
                "effects": {"happiness": 15, "hunger": -40, "health": 5},
                "icon_url": "/items/tuna.png"
            },
            {
                "name": "Milk Bowl",
                "description": "Fresh milk for your thirsty cat",
                "item_type": "food",
                "cost": 5,
                "effects": {"happiness": 10, "hunger": -20, "energy": 5},
                "icon_url": "/items/milk.png"
            },
            {
                "name": "Yarn Ball",
                "description": "A fun toy to play with",
                "item_type": "toy",
                "cost": 20,
                "effects": {"happiness": 25, "energy": -15},
                "icon_url": "/items/yarn.png",
                "is_consumable": False
            },
            {
                "name": "Feather Wand",
                "description": "Interactive toy for playtime",
                "item_type": "toy",
                "cost": 25,
                "effects": {"happiness": 30, "energy": -20},
                "icon_url": "/items/feather.png",
                "is_consumable": False
            },
            {
                "name": "Health Potion",
                "description": "Restores your cat's health",
                "item_type": "medicine",
                "cost": 30,
                "effects": {"health": 50},
                "icon_url": "/items/health_potion.png"
            },
            {
                "name": "Energy Drink",
                "description": "Boosts your cat's energy",
                "item_type": "medicine",
                "cost": 25,
                "effects": {"energy": 40},
                "icon_url": "/items/energy_drink.png"
            },
            {
                "name": "Bow Tie",
                "description": "A stylish accessory for your cat",
                "item_type": "accessory",
                "cost": 50,
                "effects": {"happiness": 5},
                "icon_url": "/items/bowtie.png",
                "is_consumable": False
            }
        ]
        
        for item_data in initial_items:
            item = Item(**item_data)
            db.add(item)
        
        db.commit()
        logger.info(f"✅ Created {len(initial_items)} initial items")
        
    except Exception as e:
        logger.error(f"❌ Error creating initial items: {e}")
        db.rollback()
    finally:
        db.close()


def create_initial_achievements():
    """Create initial achievements"""
    db = SessionLocal()
    try:
        # Check if achievements already exist
        existing = db.query(Achievement).first()
        if existing:
            logger.info("Achievements already exist, skipping...")
            return
        
        achievements = [
            # Care achievements
            {
                "name": "First Feed",
                "description": "Feed your pet for the first time",
                "category": "care",
                "requirements": {"feeds": 1},
                "currency_reward": 10,
                "experience_reward": 5,
                "rarity": "common"
            },
            {
                "name": "Caring Owner",
                "description": "Feed your pet 100 times",
                "category": "care",
                "requirements": {"feeds": 100},
                "currency_reward": 100,
                "experience_reward": 50,
                "rarity": "rare"
            },
            {
                "name": "Pet Whisperer",
                "description": "Pet your cat 50 times",
                "category": "care",
                "requirements": {"pets": 50},
                "currency_reward": 50,
                "experience_reward": 25,
                "rarity": "common"
            },
            
            # Task achievements
            {
                "name": "Task Master",
                "description": "Complete 10 tasks",
                "category": "tasks",
                "requirements": {"tasks_completed": 10},
                "currency_reward": 50,
                "experience_reward": 25,
                "rarity": "common"
            },
            {
                "name": "Productivity Pro",
                "description": "Complete 100 tasks",
                "category": "tasks",
                "requirements": {"tasks_completed": 100},
                "currency_reward": 200,
                "experience_reward": 100,
                "rarity": "epic"
            },
            {
                "name": "Streak Champion",
                "description": "Maintain a 7-day task streak",
                "category": "tasks",
                "requirements": {"streak_days": 7},
                "currency_reward": 100,
                "experience_reward": 50,
                "rarity": "rare"
            },
            
            # Social achievements
            {
                "name": "Team Player",
                "description": "Share your pet with another user",
                "category": "social",
                "requirements": {"co_owners": 1},
                "currency_reward": 30,
                "experience_reward": 15,
                "rarity": "common"
            },
            {
                "name": "Social Butterfly",
                "description": "Share pets with 5 different users",
                "category": "social",
                "requirements": {"unique_co_owners": 5},
                "currency_reward": 150,
                "experience_reward": 75,
                "rarity": "epic"
            },
            
            # Milestones
            {
                "name": "Week One",
                "description": "Keep your pet alive for 7 days",
                "category": "milestones",
                "requirements": {"days_alive": 7},
                "currency_reward": 100,
                "experience_reward": 50,
                "rarity": "common"
            },
            {
                "name": "Monthly Milestone",
                "description": "Keep your pet alive for 30 days",
                "category": "milestones",
                "requirements": {"days_alive": 30},
                "currency_reward": 500,
                "experience_reward": 250,
                "rarity": "legendary"
            }
        ]
        
        for ach_data in achievements:
            achievement = Achievement(**ach_data)
            db.add(achievement)
        
        db.commit()
        logger.info(f"✅ Created {len(achievements)} initial achievements")
        
    except Exception as e:
        logger.error(f"❌ Error creating achievements: {e}")
        db.rollback()
    finally:
        db.close()


def create_test_user():
    """Create a test user for development"""
    db = SessionLocal()
    try:
        # Check if test user exists
        existing = db.query(User).filter_by(email="test@purretys.com").first()
        if existing:
            logger.info("Test user already exists, skipping...")
            return
        
        test_user = User(
            email="test@purretys.com",
            username="testuser",
            hashed_password=get_password_hash("testpass123"),
            display_name="Test User",
            is_active=True,
            is_verified=True
        )
        
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        
        logger.info(f"✅ Created test user: {test_user.email}")
        logger.info("   Username: testuser")
        logger.info("   Password: testpass123")
        
        return test_user
        
    except Exception as e:
        logger.error(f"❌ Error creating test user: {e}")
        db.rollback()
    finally:
        db.close()


def check_database_health():
    """Check database connectivity and table existence"""
    try:
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            logger.info("✅ Database connection successful")
        
        # Check tables
        inspector = engine.inspect(engine)
        tables = inspector.get_table_names()
        
        expected_tables = [
            'users', 'pets', 'pet_ownerships', 'pet_metrics', 
            'pet_metrics_history', 'pet_activity_logs',
            'tasks', 'task_assignments', 'task_completions', 'task_comments',
            'items', 'inventory', 'transactions',
            'messages', 'notifications',
            'achievements', 'user_achievements', 'pet_invitations'
        ]
        
        missing_tables = [t for t in expected_tables if t not in tables]
        
        if missing_tables:
            logger.warning(f"⚠️  Missing tables: {missing_tables}")
            return False
        else:
            logger.info(f"✅ All {len(expected_tables)} tables exist")
            return True
            
    except Exception as e:
        logger.error(f"❌ Database health check failed: {e}")
        return False


def main():
    """Main initialization function"""
    print("\n" + "="*50)
    print("🐱 PURRETYS DATABASE INITIALIZATION")
    print("="*50 + "\n")
    
    print(f"Database: {settings.DATABASE_URL}\n")
    
    # Check if we should drop existing tables
    if len(sys.argv) > 1 and sys.argv[1] == "--fresh":
        response = input("⚠️  This will DROP all existing tables. Are you sure? (yes/no): ")
        if response.lower() == "yes":
            drop_tables()
        else:
            print("Cancelled.")
            return
    
    # Create tables
    create_tables()
    
    # Check database health
    if not check_database_health():
        logger.error("Database health check failed!")
        return
    
    # Create initial data
    print("\n📦 Creating initial data...")
    create_initial_items()
    create_initial_achievements()
    create_test_user()
    
    print("\n" + "="*50)
    print("✅ DATABASE INITIALIZATION COMPLETE!")
    print("="*50)
    print("\nYou can now run the application with:")
    print("  cd backend && python run.py")
    print("\nOr use Alembic for migrations:")
    print("  cd backend")
    print("  alembic init alembic  # First time only")
    print("  alembic revision --autogenerate -m 'Initial migration'")
    print("  alembic upgrade head")


if __name__ == "__main__":
    main()