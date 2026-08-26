from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.inventory import Warehouse, StockItem, StockMovement
from app.repositories.base import BaseRepository

class WarehouseRepository(BaseRepository[Warehouse]):
    def __init__(self, session: AsyncSession):
        super().__init__(Warehouse, session)

    async def get_by_code(self, company_id: str, code: str) -> Optional[Warehouse]:
        stmt = select(Warehouse).where(
            Warehouse.company_id == company_id,
            Warehouse.code == code,
            Warehouse.is_deleted == False
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

class StockItemRepository(BaseRepository[StockItem]):
    def __init__(self, session: AsyncSession):
        super().__init__(StockItem, session)

    async def get_stock_item(self, company_id: str, warehouse_id: str, product_id: str) -> Optional[StockItem]:
        stmt = select(StockItem).where(
            StockItem.company_id == company_id,
            StockItem.warehouse_id == warehouse_id,
            StockItem.product_id == product_id
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

class StockMovementRepository(BaseRepository[StockMovement]):
    def __init__(self, session: AsyncSession):
        super().__init__(StockMovement, session)
