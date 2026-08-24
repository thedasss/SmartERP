"""
Product and ProductCategory models.
Scoped to a company.
"""
from typing import TYPE_CHECKING
from decimal import Decimal

from sqlalchemy import Boolean, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import SoftDeleteMixin, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.company import Company


class ProductCategory(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "product_categories"

    company_id: Mapped[str] = mapped_column(ForeignKey("companies.id"), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    company: Mapped["Company"] = relationship("Company")
    products: Mapped[list["Product"]] = relationship("Product", back_populates="category")


class Product(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "products"

    company_id: Mapped[str] = mapped_column(ForeignKey("companies.id"), index=True, nullable=False)
    category_id: Mapped[str | None] = mapped_column(ForeignKey("product_categories.id"), index=True, nullable=True)
    
    sku: Mapped[str] = mapped_column(String(100), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Financials
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0.00, nullable=False)
    cost: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0.00, nullable=False)
    
    # Inventory basics
    unit_of_measure: Mapped[str] = mapped_column(String(50), default="pcs", nullable=False)
    min_stock_level: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0.00, nullable=False)
    
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    company: Mapped["Company"] = relationship("Company")
    category: Mapped["ProductCategory | None"] = relationship("ProductCategory", back_populates="products", lazy="joined")
