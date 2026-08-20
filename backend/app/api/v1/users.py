"""
User management routes.
Endpoint: /api/v1/users/*
"""
import math
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUser, require_permission
from app.core.database import get_db
from app.schemas.base import PaginatedResponse, SuccessResponse
from app.schemas.user import UserCreate, UserListItem, UserResponse, UserUpdate
from app.services.user import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "",
    response_model=PaginatedResponse[UserListItem],
    summary="List users in the current company",
    dependencies=[require_permission("user.read")],
)
async def list_users(
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
):
    service = UserService(db)
    items, total = await service.list_users(
        company_id=user.company_id,
        page=page,
        page_size=page_size,
        search=search,
    )
    total_pages = math.ceil(total / page_size)
    return PaginatedResponse(
        items=[UserListItem.model_validate(u) for u in items],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_prev=page > 1,
    )


from app.services.email import EmailService

@router.post(
    "",
    response_model=SuccessResponse[UserResponse],
    status_code=201,
    summary="Create a new user",
    dependencies=[require_permission("user.create")],
)
async def create_user(
    data: UserCreate,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    service = UserService(db)
    new_user = await service.create_user(
        data=data,
        company_id=user.company_id,
        created_by=user.id,
    )
    
    # Send mock welcome email
    await EmailService.send_welcome_email(new_user, data.password)
    
    return SuccessResponse(
        message="User created successfully",
        data=UserResponse.model_validate(new_user),
    )


@router.get(
    "/{user_id}",
    response_model=SuccessResponse[UserResponse],
    summary="Get user by ID",
    dependencies=[require_permission("user.read")],
)
async def get_user(
    user_id: str,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    service = UserService(db)
    target = await service.get_user(user_id, user.company_id)
    return SuccessResponse(data=UserResponse.model_validate(target))


@router.patch(
    "/{user_id}",
    response_model=SuccessResponse[UserResponse],
    summary="Update user",
    dependencies=[require_permission("user.update")],
)
async def update_user(
    user_id: str,
    data: UserUpdate,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    service = UserService(db)
    updated = await service.update_user(user_id, user.company_id, data)
    return SuccessResponse(
        message="User updated successfully",
        data=UserResponse.model_validate(updated),
    )


@router.delete(
    "/{user_id}",
    response_model=SuccessResponse,
    summary="Deactivate a user",
    dependencies=[require_permission("user.delete")],
)
async def deactivate_user(
    user_id: str,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    service = UserService(db)
    await service.deactivate_user(user_id, user.company_id)
    return SuccessResponse(message="User deactivated successfully")
