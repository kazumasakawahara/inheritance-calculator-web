"""User Schemas"""
from datetime import datetime
from typing import Optional

from fastapi_users import schemas
from pydantic import EmailStr


class UserRead(schemas.BaseUser[int]):
    """Schema for reading user data"""

    id: int
    email: EmailStr
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False
    full_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class UserCreate(schemas.BaseUserCreate):
    """Schema for creating a new user"""

    email: EmailStr
    password: str
    full_name: Optional[str] = None
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False
    is_verified: Optional[bool] = False


class UserUpdate(schemas.BaseUserUpdate):
    """Schema for updating user data"""

    password: Optional[str] = None
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None
    is_verified: Optional[bool] = None
