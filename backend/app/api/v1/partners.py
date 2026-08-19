from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.core.exceptions import NotFoundError
from app.models.user import User
from app.schemas.partner import (
    SupplierCreate, SupplierUpdate, SupplierResponse,
    CustomerCreate, CustomerUpdate, CustomerResponse
)
from app.services.partner import PartnerService

router = APIRouter()

# --- Suppliers ---

@router.get("/suppliers", response_model=List[SupplierResponse])
async def list_suppliers(
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = PartnerService(db)
    suppliers, _ = await service.get_suppliers(current_user.company_id, offset, limit)
    return suppliers

@router.post("/suppliers", response_model=SupplierResponse, status_code=201)
async def create_supplier(
    data: SupplierCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = PartnerService(db)
    return await service.create_supplier(data, current_user.company_id)

@router.put("/suppliers/{supplier_id}", response_model=SupplierResponse)
async def update_supplier(
    supplier_id: str,
    data: SupplierUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = PartnerService(db)
    try:
        return await service.update_supplier(supplier_id, data, current_user.company_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.delete("/suppliers/{supplier_id}", status_code=204)
async def delete_supplier(
    supplier_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = PartnerService(db)
    try:
        await service.delete_supplier(supplier_id, current_user.company_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


# --- Customers ---

@router.get("/customers", response_model=List[CustomerResponse])
async def list_customers(
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = PartnerService(db)
    customers, _ = await service.get_customers(current_user.company_id, offset, limit)
    return customers

@router.post("/customers", response_model=CustomerResponse, status_code=201)
async def create_customer(
    data: CustomerCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = PartnerService(db)
    return await service.create_customer(data, current_user.company_id)

@router.put("/customers/{customer_id}", response_model=CustomerResponse)
async def update_customer(
    customer_id: str,
    data: CustomerUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = PartnerService(db)
    try:
        return await service.update_customer(customer_id, data, current_user.company_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.delete("/customers/{customer_id}", status_code=204)
async def delete_customer(
    customer_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = PartnerService(db)
    try:
        await service.delete_customer(customer_id, current_user.company_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
