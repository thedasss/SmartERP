import enum
from typing import Optional

from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Enum as SQLEnum

from app.core.database import Base

from app.models.base import UUIDMixin, TimestampMixin, SoftDeleteMixin

class EntityType(str, enum.Enum):
    SALES_ORDER = "SALES_ORDER"
    PURCHASE_ORDER = "PURCHASE_ORDER"
    INVOICE = "INVOICE"
    PARTNER = "PARTNER"
    PRODUCT = "PRODUCT"
    GENERAL = "GENERAL"

class Document(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "documents"

    company_id: Mapped[str] = mapped_column(String(36), index=True)
    
    filename: Mapped[str] = mapped_column(String(255))
    file_path: Mapped[str] = mapped_column(String(1024))
    content_type: Mapped[str] = mapped_column(String(100))
    file_size: Mapped[int] = mapped_column(Integer)  # bytes
    
    entity_type: Mapped[EntityType] = mapped_column(SQLEnum(EntityType), default=EntityType.GENERAL, index=True)
    entity_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)
