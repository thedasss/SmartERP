from decimal import Decimal
from typing import Optional
from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.inventory import MovementType
from app.schemas.product import ProductResponse

# --- Warehouse Schemas ---

class WarehouseBase(BaseModel):
    name: str = Field(..., max_length=100)
    code: str = Field(..., max_length=50)
    location: Optional[str] = None
    is_active: bool = True

class WarehouseCreate(WarehouseBase):
    pass

class WarehouseUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    code: Optional[str] = Field(None, max_length=50)
    location: Optional[str] = None
    is_active: Optional[bool] = None

class WarehouseResponse(WarehouseBase):
    id: UUID
    company_id: UUID

    model_config = ConfigDict(from_attributes=True)


# --- StockItem Schemas ---

class StockItemResponse(BaseModel):
    id: UUID
    company_id: UUID
    warehouse_id: UUID
    product_id: UUID
    quantity: Decimal
    
    product: Optional[ProductResponse] = None
    warehouse: Optional[WarehouseResponse] = None

    model_config = ConfigDict(from_attributes=True)


# --- StockMovement Schemas ---

class StockMovementBase(BaseModel):
    product_id: UUID
    warehouse_id: UUID
    movement_type: MovementType
    quantity: Decimal = Field(..., max_digits=10, decimal_places=2)
    reference: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = None

class StockMovementCreate(StockMovementBase):
    pass

class StockMovementResponse(StockMovementBase):
    id: UUID
    company_id: UUID
    created_at: datetime
    
    product: Optional[ProductResponse] = None
    warehouse: Optional[WarehouseResponse] = None

    model_config = ConfigDict(from_attributes=True)
