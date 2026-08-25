"""
User, Role, Permission and UserRole models.
Implements RBAC with fine-grained permissions.
"""
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import SoftDeleteMixin, TimestampMixin, UUIDMixin


class Permission(Base, UUIDMixin, TimestampMixin):
    """Fine-grained permission e.g. 'inventory.read', 'purchase.approve'."""
    __tablename__ = "permissions"

    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    module: Mapped[str] = mapped_column(String(50), nullable=False)  # e.g. "inventory"
    action: Mapped[str] = mapped_column(String(50), nullable=False)  # e.g. "read"

    # Relationships
    roles: Mapped[list["RolePermission"]] = relationship(
        "RolePermission", back_populates="permission"
    )


class Role(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    """Represents a named role e.g. 'Manager', 'Warehouse Officer'."""
    __tablename__ = "roles"
    __table_args__ = (UniqueConstraint("company_id", "name", name="uq_role_company"),)

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    company_id: Mapped[str | None] = mapped_column(
        CHAR(36),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=True,  # NULL = system-level role
    )
    is_system: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    permissions: Mapped[list["RolePermission"]] = relationship(
        "RolePermission", back_populates="role", cascade="all, delete-orphan"
    )
    users: Mapped[list["UserRole"]] = relationship(
        "UserRole", back_populates="role", cascade="all, delete-orphan"
    )

    def has_permission(self, permission_name: str) -> bool:
        return any(rp.permission.name == permission_name for rp in self.permissions)


class RolePermission(Base, TimestampMixin):
    """Many-to-many join table: Role ↔ Permission."""
    __tablename__ = "role_permissions"
    __table_args__ = (
        UniqueConstraint("role_id", "permission_id", name="uq_role_permission"),
    )

    role_id: Mapped[str] = mapped_column(
        CHAR(36),
        ForeignKey("roles.id", ondelete="CASCADE"),
        primary_key=True,
    )
    permission_id: Mapped[str] = mapped_column(
        CHAR(36),
        ForeignKey("permissions.id", ondelete="CASCADE"),
        primary_key=True,
    )

    role: Mapped["Role"] = relationship("Role", back_populates="permissions")
    permission: Mapped["Permission"] = relationship(
        "Permission", back_populates="roles"
    )


class User(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    """System user belonging to a Company."""
    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint("company_id", "email", name="uq_user_email_company"),
    )

    company_id: Mapped[str] = mapped_column(
        CHAR(36),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_super_admin: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    last_login_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    failed_login_attempts: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False
    )
    locked_until: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    company: Mapped["Company"] = relationship("Company", back_populates="users")
    roles: Mapped[list["UserRole"]] = relationship(
        "UserRole", back_populates="user", cascade="all, delete-orphan"
    )
    login_history: Mapped[list["LoginHistory"]] = relationship(
        "LoginHistory", back_populates="user", cascade="all, delete-orphan"
    )

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def get_permissions(self) -> set[str]:
        """Return the set of all permission names for this user."""
        perms: set[str] = set()
        for user_role in self.roles:
            for rp in user_role.role.permissions:
                perms.add(rp.permission.name)
        return perms

    def has_permission(self, permission_name: str) -> bool:
        if self.is_super_admin:
            return True
        return permission_name in self.get_permissions()

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email!r}>"


class UserRole(Base, TimestampMixin):
    """Many-to-many join table: User ↔ Role."""
    __tablename__ = "user_roles"
    __table_args__ = (
        UniqueConstraint("user_id", "role_id", name="uq_user_role"),
    )

    user_id: Mapped[str] = mapped_column(
        CHAR(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    role_id: Mapped[str] = mapped_column(
        CHAR(36),
        ForeignKey("roles.id", ondelete="CASCADE"),
        primary_key=True,
    )
    assigned_by: Mapped[str | None] = mapped_column(CHAR(36), nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="roles")
    role: Mapped["Role"] = relationship("Role", back_populates="users")


class LoginHistory(Base, UUIDMixin):
    """Immutable record of every login attempt."""
    __tablename__ = "login_history"

    user_id: Mapped[str] = mapped_column(
        CHAR(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(Text, nullable=True)
    success: Mapped[bool] = mapped_column(Boolean, nullable=False)
    failure_reason: Mapped[str | None] = mapped_column(String(255), nullable=True)
    logged_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    user: Mapped["User"] = relationship("User", back_populates="login_history")
