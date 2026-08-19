from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query

from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User

from app.schemas.inventory import (
    WarehouseCreate, WarehouseUpdate, WarehouseResponse,
    StockItemResponse,
    StockMovementCreate, StockMovementResponse
)
from app.services.inventory import InventoryService

router = APIRouter()

def get_inventory_service(db: AsyncSession = Depends(get_db)) -> InventoryService:
    return InventoryService(db)

# --- Warehouses ---

@router.get("/warehouses", response_model=List[WarehouseResponse])
async def list_warehouses(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    service: InventoryService = Depends(get_inventory_service),
    current_user: User = Depends(get_current_user),
):
    """List all warehouses for the active company."""
    warehouses, _ = await service.get_warehouses(
        str(current_user.company_id), offset=skip, limit=limit
    )
    return warehouses

@router.post("/warehouses", response_model=WarehouseResponse, status_code=201)
async def create_warehouse(
    data: WarehouseCreate,
    service: InventoryService = Depends(get_inventory_service),
    current_user: User = Depends(get_current_user),
):
    """Create a new warehouse."""
    return await service.create_warehouse(data, str(current_user.company_id))

@router.get("/warehouses/{warehouse_id}", response_model=WarehouseResponse)
async def get_warehouse(
    warehouse_id: UUID,
    service: InventoryService = Depends(get_inventory_service),
    current_user: User = Depends(get_current_user),
):
    """Get a specific warehouse by ID."""
    return await service.get_warehouse(str(warehouse_id), str(current_user.company_id))

@router.put("/warehouses/{warehouse_id}", response_model=WarehouseResponse)
async def update_warehouse(
    warehouse_id: UUID,
    data: WarehouseUpdate,
    service: InventoryService = Depends(get_inventory_service),
    current_user: User = Depends(get_current_user),
):
    """Update a warehouse."""
    return await service.update_warehouse(str(warehouse_id), data, str(current_user.company_id))

@router.delete("/warehouses/{warehouse_id}", status_code=204)
async def delete_warehouse(
    warehouse_id: UUID,
    service: InventoryService = Depends(get_inventory_service),
    current_user: User = Depends(get_current_user),
):
    """Soft delete a warehouse."""
    await service.delete_warehouse(str(warehouse_id), str(current_user.company_id))


# --- Stock Items ---

@router.get("/stock", response_model=List[StockItemResponse])
async def list_stock(
    warehouse_id: Optional[UUID] = None,
    product_id: Optional[UUID] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    service: InventoryService = Depends(get_inventory_service),
    current_user: User = Depends(get_current_user),
):
    """List stock items, optionally filtered by warehouse or product."""
    w_id = str(warehouse_id) if warehouse_id else None
    p_id = str(product_id) if product_id else None
    
    items, _ = await service.get_stock_items(
        str(current_user.company_id), 
        warehouse_id=w_id, 
        product_id=p_id,
        offset=skip, 
        limit=limit
    )
    return items


# --- Stock Movements ---

@router.get("/movements", response_model=List[StockMovementResponse])
async def list_movements(
    warehouse_id: Optional[UUID] = None,
    product_id: Optional[UUID] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    service: InventoryService = Depends(get_inventory_service),
    current_user: User = Depends(get_current_user),
):
    """List stock movements, optionally filtered by warehouse or product."""
    w_id = str(warehouse_id) if warehouse_id else None
    p_id = str(product_id) if product_id else None
    
    movements, _ = await service.get_movements(
        str(current_user.company_id), 
        warehouse_id=w_id, 
        product_id=p_id,
        offset=skip, 
        limit=limit
    )
    return movements

@router.post("/movements", response_model=StockMovementResponse, status_code=201)
async def record_movement(
    data: StockMovementCreate,
    service: InventoryService = Depends(get_inventory_service),
    current_user: User = Depends(get_current_user),
):
    """Record a new stock movement (In, Out, Transfer, etc)."""
    return await service.record_movement(data, str(current_user.company_id))
