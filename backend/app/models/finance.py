import enum
from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from sqlalchemy import ForeignKey, String, Numeric, Text, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Enum as SQLEnum

from app.core.database import Base
from app.models.base import UUIDMixin, TimestampMixin

class InvoiceType(str, enum.Enum):
    RECEIVABLE = "RECEIVABLE"  # Sales
    PAYABLE = "PAYABLE"        # Purchases

class InvoiceStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    ISSUED = "ISSUED"
    PARTIALLY_PAID = "PARTIALLY_PAID"
    PAID = "PAID"
    CANCELLED = "CANCELLED"

class Invoice(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "invoices"

    company_id: Mapped[str] = mapped_column(String(36), index=True)
    
    # Partner (Customer or Supplier)
    # Using a generic string ID since it could map to either customers or suppliers table,
    # but practically we don't enforce a direct DB FK here because it's polymorphic.
    # We will enforce integrity in the application layer.
    partner_id: Mapped[str] = mapped_column(String(36), index=True)
    
    # Reference Order (SO or PO)
    reference_id: Mapped[Optional[str]] = mapped_column(String(36), index=True, nullable=True)
    
    invoice_number: Mapped[str] = mapped_column(String(50), index=True)
    type: Mapped[InvoiceType] = mapped_column(SQLEnum(InvoiceType))
    status: Mapped[InvoiceStatus] = mapped_column(SQLEnum(InvoiceStatus), default=InvoiceStatus.DRAFT)
    
    total_amount: Mapped[Decimal] = mapped_column(Numeric(15, 2))
    amount_paid: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=Decimal("0.00"))
    
    due_date: Mapped[Optional[datetime]] = mapped_column(Date, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    payments: Mapped[List["Payment"]] = relationship(
        "Payment", back_populates="invoice", cascade="all, delete-orphan", lazy="joined"
    )

class Payment(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "payments"

    invoice_id: Mapped[str] = mapped_column(String(36), ForeignKey("invoices.id", ondelete="CASCADE"))
    amount: Mapped[Decimal] = mapped_column(Numeric(15, 2))
    payment_date: Mapped[datetime] = mapped_column(Date)
    reference_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    invoice: Mapped["Invoice"] = relationship("Invoice", back_populates="payments")
