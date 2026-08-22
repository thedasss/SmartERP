"""
JWT and password security utilities.
"""
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional
from uuid import UUID

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import get_settings
from app.core.exceptions import AuthenticationError

settings = get_settings()

# Argon2 for password hashing (more secure than bcrypt)
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


# ── Password Hashing ─────────────────────────────────────────


def hash_password(plain: str) -> str:
    """Return the Argon2 hash of a plain-text password."""
    return pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    """Return True if plain matches hashed."""
    return pwd_context.verify(plain, hashed)


# ── Token Creation ───────────────────────────────────────────


def create_access_token(
    user_id: UUID,
    company_id: Optional[UUID] = None,
    extra_claims: Optional[Dict[str, Any]] = None,
) -> str:
    """Create a short-lived JWT access token."""
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=settings.access_token_expire_minutes)
    payload: Dict[str, Any] = {
        "sub": str(user_id),
        "type": "access",
        "iat": now,
        "exp": expire,
    }
    if company_id:
        payload["company_id"] = str(company_id)
    if extra_claims:
        payload.update(extra_claims)
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def create_refresh_token(user_id: UUID) -> str:
    """Create a long-lived JWT refresh token."""
    now = datetime.now(timezone.utc)
    expire = now + timedelta(days=settings.refresh_token_expire_days)
    payload: Dict[str, Any] = {
        "sub": str(user_id),
        "type": "refresh",
        "iat": now,
        "exp": expire,
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


# ── Token Decoding ───────────────────────────────────────────


def decode_token(token: str) -> Dict[str, Any]:
    """
    Decode and validate a JWT token.
    Raises AuthenticationError on any failure.
    """
    try:
        payload = jwt.decode(
            token, settings.jwt_secret, algorithms=[settings.jwt_algorithm]
        )
        return payload
    except JWTError as exc:
        raise AuthenticationError(f"Invalid or expired token: {exc}") from exc


def decode_access_token(token: str) -> Dict[str, Any]:
    """Decode an access token and verify its type."""
    payload = decode_token(token)
    if payload.get("type") != "access":
        raise AuthenticationError("Token is not an access token")
    return payload


def decode_refresh_token(token: str) -> Dict[str, Any]:
    """Decode a refresh token and verify its type."""
    payload = decode_token(token)
    if payload.get("type") != "refresh":
        raise AuthenticationError("Token is not a refresh token")
    return payload
