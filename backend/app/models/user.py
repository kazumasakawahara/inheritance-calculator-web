"""User Model for Authentication"""
from datetime import datetime
from typing import Optional

from fastapi_users.db import SQLAlchemyBaseUserTable
from sqlalchemy import String, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all models"""
    pass


class User(SQLAlchemyBaseUserTable[int], Base):
    """User model for authentication"""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(
        String(length=320), unique=True, index=True, nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(String(length=1024), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Additional fields
    full_name: Mapped[Optional[str]] = mapped_column(String(length=255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
