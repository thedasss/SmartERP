from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.procurement import PurchaseRequest, PurchaseOrder, GoodsReceipt
from app.repositories.base import BaseRepository

class PurchaseRequestRepository(BaseRepository[PurchaseRequest]):
    def __init__(self, session: AsyncSession):
        super().__init__(PurchaseRequest, session)
        
    async def get_by_number(self, company_id: str, pr_number: str) -> PurchaseRequest | None:
        stmt = select(self.model).where(
            self.model.company_id == company_id,
            self.model.pr_number == pr_number,
            self.model.is_deleted == False
        )
        result = await self.session.execute(stmt)
        return result.unique().scalar_one_or_none()


class PurchaseOrderRepository(BaseRepository[PurchaseOrder]):
    def __init__(self, session: AsyncSession):
        super().__init__(PurchaseOrder, session)

    async def get_by_number(self, company_id: str, po_number: str) -> PurchaseOrder | None:
        stmt = select(self.model).where(
            self.model.company_id == company_id,
            self.model.po_number == po_number,
            self.model.is_deleted == False
        )
        result = await self.session.execute(stmt)
        return result.unique().scalar_one_or_none()

class GoodsReceiptRepository(BaseRepository[GoodsReceipt]):
    def __init__(self, session: AsyncSession):
        super().__init__(GoodsReceipt, session)
