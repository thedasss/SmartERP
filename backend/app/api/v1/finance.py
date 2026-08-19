from typing import List, Any
from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.deps import get_current_user, CurrentUser, require_permission
from app.models.user import User

from app.schemas.finance import (
    InvoiceCreate,
    InvoiceResponse,
    PaymentCreate,
    PaymentResponse
)
from app.services.finance import FinanceService
from app.services.pdf import PDFService
from app.repositories.finance import InvoiceRepository
from app.services.email import EmailService

router = APIRouter()

@router.get("/invoices", response_model=List[InvoiceResponse])
async def list_invoices(
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Retrieve invoices.
    """
    inv_repo = InvoiceRepository(db)
    invoices = await inv_repo.get_all(filters={"company_id": str(current_user.company_id)}, offset=skip, limit=limit)
    return invoices[0]

@router.post("/invoices", response_model=InvoiceResponse, status_code=201)
async def create_invoice(
    data: InvoiceCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Create a new Invoice.
    """
    finance_service = FinanceService(db)
    inv = await finance_service.create_invoice(str(current_user.company_id), data)
    return inv

@router.get(
    "/invoices/{invoice_id}/pdf",
    summary="Download Invoice as PDF",
    dependencies=[require_permission("finance.read")],
)
async def download_invoice_pdf(
    invoice_id: str,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    service = FinanceService(db)
    invoice = await service.get_invoice(invoice_id, user.company_id)
    
    pdf_bytes = PDFService.generate_invoice_pdf(invoice)
    
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="Invoice_{invoice.invoice_number}.pdf"'
        }
    )

@router.post(
    "/invoices/{invoice_id}/remind",
    summary="Send Invoice Reminder",
    dependencies=[require_permission("finance.write")],
)
async def send_invoice_reminder(
    invoice_id: str,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    service = FinanceService(db)
    invoice = await service.get_invoice(invoice_id, user.company_id)
    
    # In a real system, you'd look up the customer's email from partner_id
    customer_email = f"customer_{invoice.partner_id[:8]}@example.com"
    
    await EmailService.send_invoice_reminder(invoice, customer_email)
    
    return {"success": True, "message": f"Reminder sent to {customer_email}"}

@router.post("/invoices/{invoice_id}/payments", response_model=PaymentResponse, status_code=201)
async def record_payment(
    invoice_id: str,
    data: PaymentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Record a payment against an invoice.
    """
    finance_service = FinanceService(db)
    pay = await finance_service.record_payment(str(current_user.company_id), invoice_id, data)
    return pay
