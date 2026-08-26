from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.finance import Invoice, Payment
from app.repositories.base import BaseRepository

class InvoiceRepository(BaseRepository[Invoice]):
    def __init__(self, session: AsyncSession):
        super().__init__(Invoice, session)

    async def get_by_number(self, company_id: str, invoice_number: str) -> Invoice | None:
        stmt = select(self.model).where(
            self.model.company_id == company_id,
            self.model.invoice_number == invoice_number,
            self.model.is_deleted == False
        )
        result = await self.session.execute(stmt)
        return result.unique().scalar_one_or_none()

class PaymentRepository(BaseRepository[Payment]):
    def __init__(self, session: AsyncSession):
        super().__init__(Payment, session)
