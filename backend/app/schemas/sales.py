from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, Field

from app.models.sales import SOStatus
from app.schemas.product import ProductResponse
from app.schemas.partner import CustomerResponse

# -- Sales Order Items --
class SalesOrderItemBase(BaseModel):
    product_id: str
    quantity: Decimal = Field(..., gt=0)
    unit_price: Decimal = Field(..., ge=0)

class SalesOrderItemCreate(SalesOrderItemBase):
    pass

class SalesOrderItemResponse(SalesOrderItemBase):
    id: str
    so_id: str
    shipped_quantity: Decimal
    product: Optional[ProductResponse] = None

    class Config:
        from_attributes = True

# -- Sales Orders --
class SalesOrderBase(BaseModel):
    customer_id: str
    notes: Optional[str] = None

class SalesOrderCreate(SalesOrderBase):
    items: List[SalesOrderItemCreate]

class SalesOrderResponse(SalesOrderBase):
    id: str
    company_id: str
    so_number: str
    status: SOStatus
    total_amount: Decimal
    created_at: datetime
    updated_at: datetime
    items: List[SalesOrderItemResponse] = []
    customer: Optional[CustomerResponse] = None

    class Config:
        from_attributes = True

# -- Shipments --
class ShipmentItemCreate(BaseModel):
    so_item_id: str
    quantity_shipped: Decimal = Field(..., gt=0)

class ShipmentCreate(BaseModel):
    so_id: str
    warehouse_id: str
    notes: Optional[str] = None
    items: List[ShipmentItemCreate]

class ShipmentItemResponse(BaseModel):
    id: str
    shipment_id: str
    so_item_id: str
    quantity_shipped: Decimal

    class Config:
        from_attributes = True

class ShipmentResponse(BaseModel):
    id: str
    company_id: str
    so_id: str
    warehouse_id: str
    shipment_number: str
    notes: Optional[str] = None
    created_at: datetime
    items: List[ShipmentItemResponse] = []

    class Config:
        from_attributes = True
