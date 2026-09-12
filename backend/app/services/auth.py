"""
AuthService — handles login, token refresh, logout, and current-user lookup.
Business logic lives here, not in route handlers.
"""
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.exceptions import AuthenticationError
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    verify_password,
)
from app.models.company import Company
from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.auth import TokenResponse

settings = get_settings()


class AuthService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repo = UserRepository(session)

    async def login(
        self,
        email: str,
        password: str,
        company_id: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> TokenResponse:
        """
        Authenticate a user and return JWT token pair.
        Enforces account lockout after repeated failures.
        """
        user = await self.user_repo.get_by_email(email, company_id)

        # Always run password verify to prevent timing attacks
        dummy_hash = "$argon2id$v=19$m=65536,t=3,p=4$dummy"
        password_ok = verify_password(password, user.password_hash if user else dummy_hash)

        if not user or not password_ok:
            if user:
                await self._handle_failed_login(user, ip_address, user_agent)
            raise AuthenticationError("Invalid email or password")

        if not user.is_active:
            raise AuthenticationError("Account is disabled. Contact your administrator.")

        if user.is_deleted:
            raise AuthenticationError("Account not found.")

        # Check lockout
        if user.locked_until and user.locked_until > datetime.now(timezone.utc):
            raise AuthenticationError(
                f"Account is locked until {user.locked_until.strftime('%H:%M:%S')}. Too many failed attempts."
            )

        # Reset failed attempts on success
        user.failed_login_attempts = 0
        user.locked_until = None
        user.last_login_at = datetime.now(timezone.utc)
        await self.session.flush()

        await self.user_repo.log_login(
            user_id=user.id,
            success=True,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        return self._create_token_pair(user)

    async def refresh(self, refresh_token: str) -> TokenResponse:
        """Validate refresh token and issue a new token pair."""
        try:
            payload = decode_refresh_token(refresh_token)
        except AuthenticationError:
            raise

        user_id = payload.get("sub")
        user = await self.user_repo.get_with_roles(user_id)
        if not user or not user.is_active or user.is_deleted:
            raise AuthenticationError("User not found or inactive")

        return self._create_token_pair(user)

    def _create_token_pair(self, user: User) -> TokenResponse:
        access_token = create_access_token(
            user_id=user.id,
            company_id=user.company_id,
        )
        refresh_token = create_refresh_token(user_id=user.id)
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.access_token_expire_minutes * 60,
        )

    async def _handle_failed_login(
        self,
        user: User,
        ip_address: Optional[str],
        user_agent: Optional[str],
    ) -> None:
        user.failed_login_attempts += 1
        await self.user_repo.log_login(
            user_id=user.id,
            success=False,
            ip_address=ip_address,
            user_agent=user_agent,
            failure_reason="Invalid password",
        )
        if user.failed_login_attempts >= settings.max_login_attempts:
            from datetime import timedelta
            user.locked_until = datetime.now(timezone.utc) + timedelta(
                minutes=settings.account_lockout_minutes
            )
        await self.session.flush()
