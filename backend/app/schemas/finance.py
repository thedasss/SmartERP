from datetime import datetime, date
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, Field

from app.models.finance import InvoiceType, InvoiceStatus

# -- Payments --
class PaymentBase(BaseModel):
    amount: Decimal = Field(..., gt=0)
    payment_date: date
    reference_number: Optional[str] = None
    notes: Optional[str] = None

class PaymentCreate(PaymentBase):
    pass

class PaymentResponse(PaymentBase):
    id: str
    invoice_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# -- Invoices --
class InvoiceBase(BaseModel):
    partner_id: str
    reference_id: Optional[str] = None
    type: InvoiceType
    total_amount: Decimal = Field(..., gt=0)
    due_date: Optional[date] = None
    notes: Optional[str] = None

class InvoiceCreate(InvoiceBase):
    pass

class InvoiceResponse(InvoiceBase):
    id: str
    company_id: str
    invoice_number: str
    status: InvoiceStatus
    amount_paid: Decimal
    created_at: datetime
    updated_at: datetime
    payments: List[PaymentResponse] = []
    
    # We won't embed the full Partner/Order schemas here for simplicity,
    # but the frontend can use partner_id/reference_id to fetch details if needed.

    class Config:
        from_attributes = True
