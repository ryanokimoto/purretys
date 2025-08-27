# backend/app/core/database.py
"""
Database configuration and session management
Uses SQLAlchemy for ORM and database operations
"""

from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool, QueuePool
from typing import Generator
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

# Database URL
DATABASE_URL = settings.DATABASE_URL

# Create engine based on database type
if settings.DATABASE_URL.startswith("sqlite"):
    # SQLite specific settings
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},  # Needed for SQLite
        echo=settings.DEBUG,
    )
else:
    # PostgreSQL/MySQL settings with connection pooling
    engine = create_engine(
        DATABASE_URL,
        poolclass=QueuePool,
        pool_size=settings.DATABASE_POOL_SIZE,
        max_overflow=settings.DATABASE_MAX_OVERFLOW,
        pool_pre_ping=True,  # Verify connections before using
        echo=settings.DEBUG,
    )

# Create SessionLocal class
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Create Base class for models
metadata = MetaData()
Base = declarative_base(metadata=metadata)

# Dependency to get database session
def get_db() -> Generator[Session, None, None]:
    """
    Database session dependency for FastAPI
    Yields a database session and ensures it's closed after use
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Async database setup (optional for future use)
# Only set up async engine if using PostgreSQL
if not settings.DATABASE_URL.startswith("sqlite"):
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
    from contextlib import asynccontextmanager
    
    # Convert to async URL if using PostgreSQL
    async_url = settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
    
    # Async engine
    async_engine = create_async_engine(
        async_url,
        echo=settings.DEBUG,
        pool_size=settings.DATABASE_POOL_SIZE,
        max_overflow=settings.DATABASE_MAX_OVERFLOW,
    )
    
    # Async session maker
    AsyncSessionLocal = async_sessionmaker(
        async_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    # Async session dependency
    async def get_async_db() -> AsyncSession:
        """
        Async database session dependency
        """
        async with AsyncSessionLocal() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
else:
    # Async not supported for SQLite
    async_engine = None
    AsyncSessionLocal = None
    get_async_db = None

# Database initialization functions
def init_db() -> None:
    """
    Initialize database tables
    This function should be called on application startup
    """
    try:
        # Import all models here to ensure they're registered with Base
        from app.models import user, pet, task  # noqa
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise

def drop_db() -> None:
    """
    Drop all database tables
    WARNING: This will delete all data!
    """
    try:
        Base.metadata.drop_all(bind=engine)
        logger.info("Database tables dropped successfully")
    except Exception as e:
        logger.error(f"Error dropping database tables: {e}")
        raise

# Health check function
def check_database_health() -> bool:
    """
    Check if database is accessible
    Returns True if healthy, False otherwise
    """
    try:
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        return True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False

# Context manager for database transactions
@asynccontextmanager
async def database_transaction():
    """
    Async context manager for database transactions
    Automatically commits on success and rolls back on error
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()