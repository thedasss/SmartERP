import uuid
from decimal import Decimal
from datetime import date
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.finance import InvoiceRepository, PaymentRepository
from app.schemas.finance import InvoiceCreate, PaymentCreate
from app.models.finance import Invoice, Payment, InvoiceStatus, InvoiceType

class FinanceService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.inv_repo = InvoiceRepository(session)
        self.pay_repo = PaymentRepository(session)

    def generate_invoice_number(self, inv_type: InvoiceType) -> str:
        prefix = "INV-R" if inv_type == InvoiceType.RECEIVABLE else "INV-P"
        return f"{prefix}-{str(uuid.uuid4())[:8].upper()}"

    async def create_invoice(self, company_id: str, data: InvoiceCreate) -> Invoice:
        inv_number = self.generate_invoice_number(data.type)
        
        inv_dict = data.model_dump()
        inv_dict["company_id"] = company_id
        inv_dict["invoice_number"] = inv_number
        inv_dict["status"] = InvoiceStatus.ISSUED
        inv_dict["amount_paid"] = Decimal("0.00")
        
        return await self.inv_repo.create(**inv_dict)

    async def record_payment(self, company_id: str, invoice_id: str, data: PaymentCreate) -> Payment:
        # 1. Fetch Invoice
        inv = await self.inv_repo.get_by_id(invoice_id)
        if not inv or str(inv.company_id) != company_id:
            raise HTTPException(status_code=404, detail="Invoice not found")
        
        if inv.status in (InvoiceStatus.PAID, InvoiceStatus.CANCELLED):
            raise HTTPException(status_code=400, detail=f"Cannot record payment for invoice in status: {inv.status}")
        
        # 2. Validate Payment Amount
        remaining_balance = inv.total_amount - inv.amount_paid
        if data.amount > remaining_balance:
            raise HTTPException(
                status_code=400, 
                detail=f"Payment amount ({data.amount}) exceeds remaining balance ({remaining_balance})"
            )
        
        # 3. Create Payment Record
        payment = await self.pay_repo.create(
            invoice_id=str(inv.id),
            **data.model_dump()
        )
        
        # 4. Update Invoice amount_paid and status
        new_amount_paid = inv.amount_paid + data.amount
        new_status = InvoiceStatus.PAID if new_amount_paid >= inv.total_amount else InvoiceStatus.PARTIALLY_PAID
        
        await self.inv_repo.update(
            inv, 
            amount_paid=new_amount_paid, 
            status=new_status
        )
        
        return payment
