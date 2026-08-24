"""
Inventory and Warehousing models.
"""
from typing import TYPE_CHECKING
from decimal import Decimal

from sqlalchemy import Boolean, ForeignKey, Numeric, String, Text, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.core.database import Base
from app.models.base import SoftDeleteMixin, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.company import Company
    from app.models.product import Product


class MovementType(str, enum.Enum):
    IN = "IN"           # Goods receiving, positive adjustment
    OUT = "OUT"         # Sales delivery, negative adjustment
    TRANSFER = "TRANSFER" # Moving between warehouses


class Warehouse(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "warehouses"

    company_id: Mapped[str] = mapped_column(ForeignKey("companies.id"), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    location: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    company: Mapped["Company"] = relationship("Company")


class StockItem(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "stock_items"

    company_id: Mapped[str] = mapped_column(ForeignKey("companies.id"), index=True, nullable=False)
    warehouse_id: Mapped[str] = mapped_column(ForeignKey("warehouses.id"), index=True, nullable=False)
    product_id: Mapped[str] = mapped_column(ForeignKey("products.id"), index=True, nullable=False)
    
    quantity: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0.00, nullable=False)

    # Relationships
    company: Mapped["Company"] = relationship("Company")
    warehouse: Mapped["Warehouse"] = relationship("Warehouse", lazy="joined")
    product: Mapped["Product"] = relationship("Product", lazy="joined")


class StockMovement(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "stock_movements"

    company_id: Mapped[str] = mapped_column(ForeignKey("companies.id"), index=True, nullable=False)
    product_id: Mapped[str] = mapped_column(ForeignKey("products.id"), index=True, nullable=False)
    
    # We record which warehouse it affected. If it's a transfer, we might have two movements (one out, one in).
    warehouse_id: Mapped[str] = mapped_column(ForeignKey("warehouses.id"), index=True, nullable=False)
    
    movement_type: Mapped[MovementType] = mapped_column(String(20), nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False) # positive or negative
    
    reference: Mapped[str | None] = mapped_column(String(100), nullable=True) # e.g. PO number, Invoice number
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    company: Mapped["Company"] = relationship("Company")
    product: Mapped["Product"] = relationship("Product")
    warehouse: Mapped["Warehouse"] = relationship("Warehouse")
