"""
UserRepository — database queries for users, roles, and permissions.
"""
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.user import LoginHistory, Permission, Role, RolePermission, User, UserRole
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, session: AsyncSession):
        super().__init__(User, session)

    async def get_by_email(self, email: str, company_id: str) -> Optional[User]:
        result = await self.session.execute(
            select(User)
            .options(
                selectinload(User.roles)
                .selectinload(UserRole.role)
                .selectinload(Role.permissions)
                .selectinload(RolePermission.permission)
            )
            .where(User.email == email, User.company_id == company_id, User.is_deleted.is_(False))
        )
        return result.scalar_one_or_none()

    async def get_with_roles(self, user_id: str) -> Optional[User]:
        result = await self.session.execute(
            select(User)
            .options(
                selectinload(User.roles)
                .selectinload(UserRole.role)
                .selectinload(Role.permissions)
                .selectinload(RolePermission.permission)
            )
            .where(User.id == user_id, User.is_deleted.is_(False))
        )
        return result.scalar_one_or_none()

    async def get_by_company(
        self,
        company_id: str,
        offset: int = 0,
        limit: int = 20,
        search: Optional[str] = None,
    ) -> tuple[List[User], int]:
        from sqlalchemy import func, or_

        query = (
            select(User)
            .where(User.company_id == company_id, User.is_deleted.is_(False))
        )
        if search:
            like = f"%{search}%"
            query = query.where(
                or_(
                    User.email.ilike(like),
                    User.first_name.ilike(like),
                    User.last_name.ilike(like),
                )
            )
        count_query = select(func.count()).select_from(query.subquery())
        total = (await self.session.execute(count_query)).scalar_one()
        result = await self.session.execute(query.offset(offset).limit(limit))
        return list(result.scalars().all()), total

    async def assign_role(self, user_id: str, role_id: str, assigned_by: str) -> None:
        user_role = UserRole(user_id=user_id, role_id=role_id, assigned_by=assigned_by)
        self.session.add(user_role)
        await self.session.flush()

    async def remove_role(self, user_id: str, role_id: str) -> None:
        result = await self.session.execute(
            select(UserRole).where(
                UserRole.user_id == user_id, UserRole.role_id == role_id
            )
        )
        ur = result.scalar_one_or_none()
        if ur:
            await self.session.delete(ur)
            await self.session.flush()

    async def log_login(
        self,
        user_id: str,
        success: bool,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        failure_reason: Optional[str] = None,
    ) -> None:
        from datetime import datetime, timezone
        entry = LoginHistory(
            user_id=user_id,
            success=success,
            ip_address=ip_address,
            user_agent=user_agent,
            failure_reason=failure_reason,
            logged_at=datetime.now(timezone.utc),
        )
        self.session.add(entry)
        await self.session.flush()


class RoleRepository(BaseRepository[Role]):
    def __init__(self, session: AsyncSession):
        super().__init__(Role, session)

    async def get_by_name(self, name: str, company_id: str) -> Optional[Role]:
        result = await self.session.execute(
            select(Role).where(
                Role.name == name,
                Role.company_id == company_id,
                Role.is_deleted.is_(False),
            )
        )
        return result.scalar_one_or_none()

    async def get_with_permissions(self, role_id: str) -> Optional[Role]:
        result = await self.session.execute(
            select(Role)
            .options(
                selectinload(Role.permissions).selectinload(RolePermission.permission)
            )
            .where(Role.id == role_id, Role.is_deleted.is_(False))
        )
        return result.scalar_one_or_none()

    async def get_company_roles(self, company_id: str) -> List[Role]:
        result = await self.session.execute(
            select(Role)
            .options(
                selectinload(Role.permissions).selectinload(RolePermission.permission)
            )
            .where(
                (Role.company_id == company_id) | (Role.is_system.is_(True)),
                Role.is_deleted.is_(False),
            )
        )
        return list(result.scalars().all())

    async def add_permission(self, role_id: str, permission_id: str) -> None:
        rp = RolePermission(role_id=role_id, permission_id=permission_id)
        self.session.add(rp)
        await self.session.flush()


class PermissionRepository(BaseRepository[Permission]):
    def __init__(self, session: AsyncSession):
        super().__init__(Permission, session)

    async def get_by_name(self, name: str) -> Optional[Permission]:
        result = await self.session.execute(
            select(Permission).where(Permission.name == name)
        )
        return result.scalar_one_or_none()

    async def get_all_permissions(self) -> List[Permission]:
        result = await self.session.execute(select(Permission).order_by(Permission.module, Permission.action))
        return list(result.scalars().all())
