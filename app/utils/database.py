# -------------------------------------------
# Author: Nils Gies
# -------------------------------------------
"""Async database utility functions and session management."""
# -------------------------------------------

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
)
from typing import AsyncGenerator
from sqlalchemy.orm import declarative_base

ASYNC_DB_URL = "sqlite+aiosqlite:///./test_items.db"

# Global async engine with optimized pool settings
async_engine: AsyncEngine = create_async_engine(
    ASYNC_DB_URL,
    echo=False,  # Disable SQL query logging
    future=True,  # Use SQLAlchemy 2.0 style
    pool_pre_ping=True,  # Verify connections before using
    pool_size=20,  # Max connections in pool (default: 5)
    max_overflow=10,  # Additional connections when pool exhausted (default: 10)
    pool_recycle=3600,  # Recycle connections after 1 hour
)

# Global session factory
AsyncSessionLocal = async_sessionmaker(
    async_engine,
    expire_on_commit=False,
    autoflush=False,
    class_=AsyncSession,
)

Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get async database session."""
    async with AsyncSessionLocal() as session:
        yield session


async def create_tables():
    """Create all tables in the database.
    Import all models in main.py before app startup.
    """
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        # run_sync because create_all is synchronous
        # to avoid blocking the event loop, run_sync is used to run it in a separate thread
        # returns control to the async context when done


async def drop_tables():
    """Drop all tables in the database."""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
