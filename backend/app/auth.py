"""Authentication Configuration"""
from typing import Optional

from fastapi import Depends, Request
from fastapi_users import BaseUserManager, FastAPIUsers, IntegerIDMixin
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)
from fastapi_users.db import SQLAlchemyUserDatabase

from app.config import settings
from app.models.user import User
from app.db import get_user_db


class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    """User manager for authentication"""

    reset_password_token_secret = settings.secret_key
    verification_token_secret = settings.secret_key

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        """Called after user registration"""
        print(f"User {user.id} has registered.")

    async def on_after_forgot_password(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        """Called after user requests password reset"""
        print(f"User {user.id} has forgot their password. Reset token: {token}")

    async def on_after_request_verify(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        """Called after user requests verification"""
        print(f"Verification requested for user {user.id}. Verification token: {token}")


async def get_user_manager(user_db: SQLAlchemyUserDatabase = Depends(get_user_db)):
    """Get user manager"""
    yield UserManager(user_db)


def get_jwt_strategy() -> JWTStrategy:
    """Get JWT strategy"""
    return JWTStrategy(
        secret=settings.secret_key,
        lifetime_seconds=settings.access_token_expire_minutes * 60,
    )


# Bearer transport (JWT in Authorization header)
bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")

# Authentication backend
auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

# FastAPI Users instance
fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)

# Current user dependency
current_active_user = fastapi_users.current_user(active=True)
