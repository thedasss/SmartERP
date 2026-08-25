import enum
from decimal import Decimal
from typing import List, Optional

from sqlalchemy import ForeignKey, String, Numeric, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Enum as SQLEnum

from app.core.database import Base
from app.models.base import UUIDMixin, TimestampMixin

class SOStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    CONFIRMED = "CONFIRMED"
    PARTIALLY_SHIPPED = "PARTIALLY_SHIPPED"
    SHIPPED = "SHIPPED"
    CANCELLED = "CANCELLED"

class SalesOrder(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "sales_orders"

    company_id: Mapped[str] = mapped_column(String(36), index=True)
    customer_id: Mapped[str] = mapped_column(String(36), ForeignKey("customers.id"))
    so_number: Mapped[str] = mapped_column(String(50), index=True)
    status: Mapped[SOStatus] = mapped_column(SQLEnum(SOStatus), default=SOStatus.DRAFT)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=Decimal("0.00"))
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    items: Mapped[List["SalesOrderItem"]] = relationship(
        "SalesOrderItem", back_populates="order", cascade="all, delete-orphan", lazy="joined"
    )
    customer = relationship("Customer", lazy="joined")

class SalesOrderItem(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "sales_order_items"

    so_id: Mapped[str] = mapped_column(String(36), ForeignKey("sales_orders.id", ondelete="CASCADE"))
    product_id: Mapped[str] = mapped_column(String(36), ForeignKey("products.id"))
    quantity: Mapped[Decimal] = mapped_column(Numeric(15, 2))
    unit_price: Mapped[Decimal] = mapped_column(Numeric(15, 2))
    shipped_quantity: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=Decimal("0.00"))

    order: Mapped["SalesOrder"] = relationship("SalesOrder", back_populates="items")
    product = relationship("Product", lazy="joined")

class Shipment(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "shipments"

    company_id: Mapped[str] = mapped_column(String(36), index=True)
    so_id: Mapped[str] = mapped_column(String(36), ForeignKey("sales_orders.id"))
    warehouse_id: Mapped[str] = mapped_column(String(36), ForeignKey("warehouses.id"))
    shipment_number: Mapped[str] = mapped_column(String(50), index=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    items: Mapped[List["ShipmentItem"]] = relationship(
        "ShipmentItem", back_populates="shipment", cascade="all, delete-orphan", lazy="joined"
    )
    order = relationship("SalesOrder", lazy="joined")
    warehouse = relationship("Warehouse", lazy="joined")

class ShipmentItem(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "shipment_items"

    shipment_id: Mapped[str] = mapped_column(String(36), ForeignKey("shipments.id", ondelete="CASCADE"))
    so_item_id: Mapped[str] = mapped_column(String(36), ForeignKey("sales_order_items.id"))
    quantity_shipped: Mapped[Decimal] = mapped_column(Numeric(15, 2))

    shipment: Mapped["Shipment"] = relationship("Shipment", back_populates="items")
    so_item = relationship("SalesOrderItem", lazy="joined")
