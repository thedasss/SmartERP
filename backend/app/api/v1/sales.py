from typing import List, Any
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User

from app.schemas.sales import (
    SalesOrderCreate,
    SalesOrderResponse,
    ShipmentCreate,
    ShipmentResponse
)
from app.services.sales import SalesService
from app.repositories.sales import SalesOrderRepository

router = APIRouter()

@router.get("/orders", response_model=List[SalesOrderResponse])
async def list_sales_orders(
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Retrieve sales orders.
    """
    so_repo = SalesOrderRepository(db)
    sos = await so_repo.get_all(filters={"company_id": str(current_user.company_id)}, offset=skip, limit=limit)
    return sos[0]

@router.post("/orders", response_model=SalesOrderResponse, status_code=201)
async def create_sales_order(
    data: SalesOrderCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Create a new Sales Order.
    """
    sales_service = SalesService(db)
    so = await sales_service.create_sales_order(str(current_user.company_id), data)
    return so

@router.post("/orders/{so_id}/ship", response_model=ShipmentResponse, status_code=201)
async def ship_goods(
    so_id: str,
    data: ShipmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Ship goods against a Sales Order, updating inventory.
    """
    # Ensure URL matches payload
    data.so_id = so_id
    sales_service = SalesService(db)
    shp = await sales_service.ship_goods(str(current_user.company_id), data)
    return shp
