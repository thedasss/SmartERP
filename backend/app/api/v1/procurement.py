from typing import List, Any
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User

from app.schemas.procurement import (
    PurchaseOrderCreate,
    PurchaseOrderResponse,
    GoodsReceiptCreate,
    GoodsReceiptResponse
)
from app.services.procurement import ProcurementService
from app.repositories.procurement import PurchaseOrderRepository

router = APIRouter()

@router.get("/orders", response_model=List[PurchaseOrderResponse])
async def list_purchase_orders(
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Retrieve purchase orders.
    """
    po_repo = PurchaseOrderRepository(db)
    pos = await po_repo.get_all(filters={"company_id": str(current_user.company_id)}, offset=skip, limit=limit)
    return pos[0]

@router.post("/orders", response_model=PurchaseOrderResponse, status_code=201)
async def create_purchase_order(
    data: PurchaseOrderCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Create a new Purchase Order.
    """
    procurement_service = ProcurementService(db)
    po = await procurement_service.create_purchase_order(db, str(current_user.company_id), data)
    return po

@router.post("/orders/{po_id}/receive", response_model=GoodsReceiptResponse, status_code=201)
async def receive_goods(
    po_id: str,
    data: GoodsReceiptCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Receive goods against a Purchase Order, updating inventory.
    """
    # Ensure URL matches payload
    data.po_id = po_id
    procurement_service = ProcurementService(db)
    gr = await procurement_service.receive_goods(db, str(current_user.company_id), data)
    return gr
