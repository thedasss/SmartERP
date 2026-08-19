from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User

from app.schemas.reports import (
    SalesTrendResponse,
    InventoryValuationResponse,
    CashFlowResponse
)
from app.services.reports import ReportService

router = APIRouter()

@router.get("/sales/trend", response_model=SalesTrendResponse)
async def get_sales_trend(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get aggregated sales grouped by date.
    """
    svc = ReportService(db)
    data = await svc.get_sales_trend(str(current_user.company_id))
    return {"data": data}

@router.get("/inventory/valuation", response_model=InventoryValuationResponse)
async def get_inventory_valuation(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get inventory valuation grouped by product category.
    """
    svc = ReportService(db)
    data = await svc.get_inventory_valuation(str(current_user.company_id))
    return {"data": data}

@router.get("/finance/cashflow", response_model=CashFlowResponse)
async def get_cashflow(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get cash flow (money in/out) grouped by date.
    """
    svc = ReportService(db)
    data = await svc.get_cash_flow(str(current_user.company_id))
    return {"data": data}
