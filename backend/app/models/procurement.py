import enum
from typing import List, Optional
from decimal import Decimal
from sqlalchemy import String, ForeignKey, Enum as SQLEnum, Numeric, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import UUIDMixin, TimestampMixin

class PRStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"

class POStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    ISSUED = "ISSUED"
    PARTIALLY_RECEIVED = "PARTIALLY_RECEIVED"
    RECEIVED = "RECEIVED"
    CANCELLED = "CANCELLED"

class PurchaseRequest(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "purchase_requests"

    company_id: Mapped[str] = mapped_column(String(36), index=True)
    pr_number: Mapped[str] = mapped_column(String(50), index=True)
    status: Mapped[PRStatus] = mapped_column(SQLEnum(PRStatus), default=PRStatus.DRAFT)
    requester_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("users.id"), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    items: Mapped[List["PurchaseRequestItem"]] = relationship("PurchaseRequestItem", back_populates="request", cascade="all, delete-orphan", lazy="joined")
    requester = relationship("User", lazy="joined")

class PurchaseRequestItem(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "purchase_request_items"

    pr_id: Mapped[str] = mapped_column(String(36), ForeignKey("purchase_requests.id", ondelete="CASCADE"))
    product_id: Mapped[str] = mapped_column(String(36), ForeignKey("products.id"))
    quantity: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    request: Mapped["PurchaseRequest"] = relationship("PurchaseRequest", back_populates="items")
    product = relationship("Product", lazy="joined")

class PurchaseOrder(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "purchase_orders"

    company_id: Mapped[str] = mapped_column(String(36), index=True)
    supplier_id: Mapped[str] = mapped_column(String(36), ForeignKey("suppliers.id"))
    po_number: Mapped[str] = mapped_column(String(50), index=True)
    status: Mapped[POStatus] = mapped_column(SQLEnum(POStatus), default=POStatus.DRAFT)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=Decimal("0.00"))
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    pr_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("purchase_requests.id"), nullable=True)

    items: Mapped[List["PurchaseOrderItem"]] = relationship("PurchaseOrderItem", back_populates="order", cascade="all, delete-orphan", lazy="joined")
    supplier = relationship("Supplier", lazy="joined")

class PurchaseOrderItem(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "purchase_order_items"

    po_id: Mapped[str] = mapped_column(String(36), ForeignKey("purchase_orders.id", ondelete="CASCADE"))
    product_id: Mapped[str] = mapped_column(String(36), ForeignKey("products.id"))
    quantity: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    unit_price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    received_quantity: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("0.00"))

    order: Mapped["PurchaseOrder"] = relationship("PurchaseOrder", back_populates="items")
    product = relationship("Product", lazy="joined")

class GoodsReceipt(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "goods_receipts"

    company_id: Mapped[str] = mapped_column(String(36), index=True)
    po_id: Mapped[str] = mapped_column(String(36), ForeignKey("purchase_orders.id"))
    warehouse_id: Mapped[str] = mapped_column(String(36), ForeignKey("warehouses.id"))
    receipt_number: Mapped[str] = mapped_column(String(50), index=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    items: Mapped[List["GoodsReceiptItem"]] = relationship("GoodsReceiptItem", back_populates="receipt", cascade="all, delete-orphan", lazy="joined")
    order = relationship("PurchaseOrder", lazy="joined")
    warehouse = relationship("Warehouse", lazy="joined")

class GoodsReceiptItem(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "goods_receipt_items"

    receipt_id: Mapped[str] = mapped_column(String(36), ForeignKey("goods_receipts.id", ondelete="CASCADE"))
    po_item_id: Mapped[str] = mapped_column(String(36), ForeignKey("purchase_order_items.id"))
    quantity_received: Mapped[Decimal] = mapped_column(Numeric(10, 2))

    receipt: Mapped["GoodsReceipt"] = relationship("GoodsReceipt", back_populates="items")
    po_item = relationship("PurchaseOrderItem", lazy="joined")
