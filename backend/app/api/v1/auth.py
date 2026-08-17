"""
Auth routes: login, refresh, logout, current user.
Endpoint: /api/v1/auth/*
"""
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Header, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUser, get_client_ip
from app.core.database import get_db
from app.schemas.auth import (
    LoginRequest,
    LogoutRequest,
    RefreshRequest,
    TokenResponse,
)
from app.schemas.user import CurrentUserResponse
from app.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login with email and password",
    description="Authenticate using company email and password. Returns JWT access and refresh tokens.",
)
async def login(
    data: LoginRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    x_company_id: Optional[str] = Header(None, alias="X-Company-ID"),
):
    """
    Login endpoint.
    The X-Company-ID header identifies which company the user belongs to.
    In Phase 1, we seed a default company — clients can omit this header
    and a fallback lookup by email will find the correct company.
    """
    # Temporary: look up company by email if X-Company-ID not provided
    if not x_company_id:
        from sqlalchemy import select
        from app.models.user import User
        result = await db.execute(
            select(User.company_id).where(User.email == data.email.lower()).limit(1)
        )
        row = result.scalar_one_or_none()
        if not row:
            from app.core.exceptions import AuthenticationError
            raise AuthenticationError("Invalid email or password")
        x_company_id = row

    ip = get_client_ip(request)
    user_agent = request.headers.get("User-Agent")
    service = AuthService(db)
    return await service.login(
        email=data.email,
        password=data.password,
        company_id=x_company_id,
        ip_address=ip,
        user_agent=user_agent,
    )


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh access token",
)
async def refresh_token(data: RefreshRequest, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    return await service.refresh(data.refresh_token)


@router.post(
    "/logout",
    summary="Logout (client-side token invalidation)",
)
async def logout(data: LogoutRequest, user: CurrentUser):
    """
    Stateless JWT logout — client must discard tokens.
    Future: add refresh token to a Redis denylist for true invalidation.
    """
    return {"success": True, "message": "Logged out successfully"}


@router.get(
    "/me",
    response_model=CurrentUserResponse,
    summary="Get current authenticated user",
)
async def get_me(user: CurrentUser):
    permissions = list(user.get_permissions())
    role_names = [ur.role.name for ur in user.roles]
    return CurrentUserResponse(
        id=user.id,
        company_id=user.company_id,
        email=user.email,
        full_name=user.full_name,
        is_active=user.is_active,
        is_super_admin=user.is_super_admin,
        permissions=permissions,
        roles=role_names,
    )
