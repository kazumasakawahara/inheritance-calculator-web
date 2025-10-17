"""Database Configuration"""
from typing import AsyncGenerator

from fastapi import Depends
from fastapi_users.db import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings
from app.models.user import User, Base

# Create async engine
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
)

# Create async session maker
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def create_db_and_tables():
    """Create database tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Get async database session"""
    async with async_session_maker() as session:
        yield session


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    """Get user database for FastAPI-Users"""
    yield SQLAlchemyUserDatabase(session, User)
