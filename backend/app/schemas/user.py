"""
User, Role, and Permission Pydantic schemas.
"""
from datetime import datetime
from typing import List, Optional

from pydantic import EmailStr, field_validator

from app.schemas.base import BaseSchema


# ── Permission Schemas ────────────────────────────────────────


class PermissionResponse(BaseSchema):
    id: str
    name: str
    description: Optional[str]
    module: str
    action: str
    created_at: datetime


# ── Role Schemas ──────────────────────────────────────────────


class RoleCreate(BaseSchema):
    name: str
    description: Optional[str] = None


class RoleUpdate(BaseSchema):
    name: Optional[str] = None
    description: Optional[str] = None


class RoleResponse(BaseSchema):
    id: str
    name: str
    description: Optional[str]
    company_id: Optional[str]
    is_system: bool
    created_at: datetime
    permissions: List[PermissionResponse] = []


# ── User Schemas ──────────────────────────────────────────────


class UserCreate(BaseSchema):
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    phone: Optional[str] = None
    role_ids: List[str] = []

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one number")
        return v

    @field_validator("first_name", "last_name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Name cannot be blank")
        return v.strip()


class UserUpdate(BaseSchema):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    is_active: Optional[bool] = None


class UserResponse(BaseSchema):
    id: str
    company_id: str
    email: str
    first_name: str
    last_name: str
    full_name: str
    phone: Optional[str]
    avatar_url: Optional[str]
    is_active: bool
    is_super_admin: bool
    last_login_at: Optional[datetime]
    created_at: datetime
    roles: List[RoleResponse] = []

    @classmethod
    def model_validate(cls, obj, **kwargs):
        # Flatten user_roles → roles
        if hasattr(obj, "roles"):
            obj.__dict__["roles"] = [ur.role for ur in obj.roles]
        return super().model_validate(obj, **kwargs)


class UserListItem(BaseSchema):
    """Lightweight user representation for list endpoints."""
    id: str
    email: str
    first_name: str
    last_name: str
    full_name: str
    is_active: bool
    is_super_admin: bool
    last_login_at: Optional[datetime]
    created_at: datetime


class CurrentUserResponse(BaseSchema):
    """Returned by GET /auth/me — includes permissions list."""
    id: str
    company_id: str
    email: str
    full_name: str
    is_active: bool
    is_super_admin: bool
    permissions: List[str] = []
    roles: List[str] = []
