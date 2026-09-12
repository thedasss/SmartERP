from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, Field

from app.models.procurement import PRStatus, POStatus
from app.schemas.product import ProductResponse
from app.schemas.partner import SupplierResponse

# -- Purchase Request Items --
class PurchaseRequestItemBase(BaseModel):
    product_id: str
    quantity: Decimal = Field(..., gt=0)
    notes: Optional[str] = None

class PurchaseRequestItemCreate(PurchaseRequestItemBase):
    pass

class PurchaseRequestItemResponse(PurchaseRequestItemBase):
    id: str
    pr_id: str
    product: Optional[ProductResponse] = None

    class Config:
        from_attributes = True

# -- Purchase Requests --
class PurchaseRequestBase(BaseModel):
    notes: Optional[str] = None

class PurchaseRequestCreate(PurchaseRequestBase):
    items: List[PurchaseRequestItemCreate]

class PurchaseRequestResponse(PurchaseRequestBase):
    id: str
    company_id: str
    pr_number: str
    status: PRStatus
    requester_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    items: List[PurchaseRequestItemResponse] = []

    class Config:
        from_attributes = True

# -- Purchase Order Items --
class PurchaseOrderItemBase(BaseModel):
    product_id: str
    quantity: Decimal = Field(..., gt=0)
    unit_price: Decimal = Field(..., ge=0)

class PurchaseOrderItemCreate(PurchaseOrderItemBase):
    pass

class PurchaseOrderItemResponse(PurchaseOrderItemBase):
    id: str
    po_id: str
    received_quantity: Decimal
    product: Optional[ProductResponse] = None

    class Config:
        from_attributes = True

# -- Purchase Orders --
class PurchaseOrderBase(BaseModel):
    supplier_id: str
    notes: Optional[str] = None
    pr_id: Optional[str] = None

class PurchaseOrderCreate(PurchaseOrderBase):
    items: List[PurchaseOrderItemCreate]

class PurchaseOrderResponse(PurchaseOrderBase):
    id: str
    company_id: str
    po_number: str
    status: POStatus
    total_amount: Decimal
    created_at: datetime
    updated_at: datetime
    items: List[PurchaseOrderItemResponse] = []
    supplier: Optional[SupplierResponse] = None

    class Config:
        from_attributes = True

# -- Goods Receipts --
class GoodsReceiptItemCreate(BaseModel):
    po_item_id: str
    quantity_received: Decimal = Field(..., gt=0)

class GoodsReceiptCreate(BaseModel):
    po_id: str
    warehouse_id: str
    notes: Optional[str] = None
    items: List[GoodsReceiptItemCreate]

class GoodsReceiptItemResponse(BaseModel):
    id: str
    receipt_id: str
    po_item_id: str
    quantity_received: Decimal

    class Config:
        from_attributes = True

class GoodsReceiptResponse(BaseModel):
    id: str
    company_id: str
    po_id: str
    warehouse_id: str
    receipt_number: str
    notes: Optional[str] = None
    created_at: datetime
    items: List[GoodsReceiptItemResponse] = []

    class Config:
        from_attributes = True
