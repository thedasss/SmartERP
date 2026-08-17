"""
FastAPI dependency functions for authentication and authorization.
Use these as Depends() in route handlers.
"""
from typing import Annotated, Optional

from fastapi import Depends, Header, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import AuthenticationError, AuthorizationError
from app.core.security import decode_access_token
from app.models.user import User
from app.repositories.user import UserRepository, RoleRepository, RolePermission

bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Annotated[Optional[HTTPAuthorizationCredentials], Depends(bearer_scheme)],
    db: AsyncSession = Depends(get_db),
) -> User:
    """Extract and validate JWT, return the authenticated User."""
    if not credentials:
        raise AuthenticationError("Authorization header missing")

    payload = decode_access_token(credentials.credentials)
    user_id = payload.get("sub")
    if not user_id:
        raise AuthenticationError("Invalid token payload")

    user_repo = UserRepository(db)
    user = await user_repo.get_with_roles(user_id)
    if not user:
        raise AuthenticationError("User not found")
    if not user.is_active or user.is_deleted:
        raise AuthenticationError("Account is inactive or deleted")

    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def require_permission(permission: str):
    """
    Returns a FastAPI dependency that checks if the current user
    has the specified permission.

    Usage:
        @router.get("/", dependencies=[Depends(require_permission("inventory.read"))])
    """
    async def _check(user: CurrentUser) -> User:
        if not user.has_permission(permission):
            raise AuthorizationError(
                f"Permission '{permission}' is required to perform this action."
            )
        return user

    return Depends(_check)


def require_super_admin(user: CurrentUser) -> User:
    """Dependency: only super admins can proceed."""
    if not user.is_super_admin:
        raise AuthorizationError("Super admin access required")
    return user


def get_client_ip(request: Request) -> Optional[str]:
    """Extract the real client IP from request headers."""
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.client.host if request.client else None
