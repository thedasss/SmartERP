"""
UserService — business logic for user and role management.
"""
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, NotFoundError, AuthorizationError
from app.core.security import hash_password
from app.models.user import User, Role
from app.repositories.user import PermissionRepository, RoleRepository, UserRepository
from app.schemas.user import UserCreate, UserUpdate


class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repo = UserRepository(session)
        self.role_repo = RoleRepository(session)
        self.perm_repo = PermissionRepository(session)

    async def create_user(
        self,
        data: UserCreate,
        company_id: str,
        created_by: str,
    ) -> User:
        # Check for duplicate email within company
        existing = await self.user_repo.get_by_email(data.email, company_id)
        if existing:
            raise ConflictError(
                f"A user with email '{data.email}' already exists in this company.",
                error_code="DUPLICATE_USER_EMAIL",
            )

        user = await self.user_repo.create(
            company_id=company_id,
            email=data.email.lower().strip(),
            password_hash=hash_password(data.password),
            first_name=data.first_name.strip(),
            last_name=data.last_name.strip(),
            phone=data.phone,
        )

        # Assign roles
        for role_id in data.role_ids:
            role = await self.role_repo.get_with_permissions(role_id)
            if not role:
                raise NotFoundError("Role", role_id)
            # Ensure role belongs to this company or is a system role
            if role.company_id and role.company_id != company_id:
                raise AuthorizationError("Cannot assign role from a different company")
            await self.user_repo.assign_role(user.id, role_id, created_by)

        return await self.user_repo.get_with_roles(user.id)

    async def get_user(self, user_id: str, company_id: str) -> User:
        user = await self.user_repo.get_with_roles(user_id)
        if not user or user.company_id != company_id:
            raise NotFoundError("User", user_id)
        return user

    async def list_users(
        self,
        company_id: str,
        page: int = 1,
        page_size: int = 20,
        search: Optional[str] = None,
    ) -> tuple[List[User], int]:
        offset = (page - 1) * page_size
        return await self.user_repo.get_by_company(
            company_id=company_id,
            offset=offset,
            limit=page_size,
            search=search,
        )

    async def update_user(
        self, user_id: str, company_id: str, data: UserUpdate
    ) -> User:
        user = await self.user_repo.get_with_roles(user_id)
        if not user or user.company_id != company_id:
            raise NotFoundError("User", user_id)

        update_data = data.model_dump(exclude_none=True)
        await self.user_repo.update(user, **update_data)
        return await self.user_repo.get_with_roles(user_id)

    async def deactivate_user(self, user_id: str, company_id: str) -> User:
        user = await self.user_repo.get_by_id(user_id)
        if not user or user.company_id != company_id:
            raise NotFoundError("User", user_id)
        if user.is_super_admin:
            raise AuthorizationError("Cannot deactivate a super admin user")
        user.is_active = False
        await self.session.flush()
        return user

    async def assign_role_to_user(
        self, user_id: str, role_id: str, company_id: str, assigned_by: str
    ) -> User:
        user = await self.user_repo.get_by_id(user_id)
        if not user or user.company_id != company_id:
            raise NotFoundError("User", user_id)
        role = await self.role_repo.get_by_id(role_id)
        if not role:
            raise NotFoundError("Role", role_id)
        if role.company_id and role.company_id != company_id:
            raise AuthorizationError("Role belongs to a different company")
        await self.user_repo.assign_role(user_id, role_id, assigned_by)
        return await self.user_repo.get_with_roles(user_id)

    async def remove_role_from_user(
        self, user_id: str, role_id: str, company_id: str
    ) -> User:
        user = await self.user_repo.get_by_id(user_id)
        if not user or user.company_id != company_id:
            raise NotFoundError("User", user_id)
        await self.user_repo.remove_role(user_id, role_id)
        return await self.user_repo.get_with_roles(user_id)
