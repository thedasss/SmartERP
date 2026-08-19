from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.core.exceptions import ConflictError, NotFoundError
from app.models.user import User
from app.schemas.product import (
    ProductCreate, ProductUpdate, ProductResponse,
    ProductCategoryCreate, ProductCategoryUpdate, ProductCategoryResponse
)
from app.services.product import ProductService

router = APIRouter()


# --- Categories ---

@router.get("/categories", response_model=List[ProductCategoryResponse])
async def list_categories(
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ProductService(db)
    categories, _ = await service.get_categories(current_user.company_id, offset, limit)
    return categories

@router.post("/categories", response_model=ProductCategoryResponse, status_code=201)
async def create_category(
    data: ProductCategoryCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # TODO: Require specific permissions (e.g. "manage_products")
    service = ProductService(db)
    return await service.create_category(data, current_user.company_id)

@router.put("/categories/{category_id}", response_model=ProductCategoryResponse)
async def update_category(
    category_id: str,
    data: ProductCategoryUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ProductService(db)
    try:
        return await service.update_category(category_id, data, current_user.company_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.delete("/categories/{category_id}", status_code=204)
async def delete_category(
    category_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ProductService(db)
    try:
        await service.delete_category(category_id, current_user.company_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ConflictError as e:
        raise HTTPException(status_code=409, detail=str(e))


# --- Products ---

@router.get("", response_model=List[ProductResponse])
async def list_products(
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ProductService(db)
    products, _ = await service.get_products(current_user.company_id, offset, limit)
    return products

@router.post("", response_model=ProductResponse, status_code=201)
async def create_product(
    data: ProductCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ProductService(db)
    try:
        return await service.create_product(data, current_user.company_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ConflictError as e:
        raise HTTPException(status_code=409, detail=str(e))

@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: str,
    data: ProductUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ProductService(db)
    try:
        return await service.update_product(product_id, data, current_user.company_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ConflictError as e:
        raise HTTPException(status_code=409, detail=str(e))

@router.delete("/{product_id}", status_code=204)
async def delete_product(
    product_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ProductService(db)
    try:
        await service.delete_product(product_id, current_user.company_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
