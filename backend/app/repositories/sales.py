from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.sales import SalesOrder, Shipment
from app.repositories.base import BaseRepository

class SalesOrderRepository(BaseRepository[SalesOrder]):
    def __init__(self, session: AsyncSession):
        super().__init__(SalesOrder, session)

    async def get_by_number(self, company_id: str, so_number: str) -> SalesOrder | None:
        stmt = select(self.model).where(
            self.model.company_id == company_id,
            self.model.so_number == so_number,
            self.model.is_deleted == False
        )
        result = await self.session.execute(stmt)
        return result.unique().scalar_one_or_none()

class ShipmentRepository(BaseRepository[Shipment]):
    def __init__(self, session: AsyncSession):
        super().__init__(Shipment, session)
