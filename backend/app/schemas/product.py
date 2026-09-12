from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ProductCategoryBase(BaseModel):
    name: str = Field(..., max_length=100)
    description: Optional[str] = None
    is_active: bool = True


class ProductCategoryCreate(ProductCategoryBase):
    pass


class ProductCategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    is_active: Optional[bool] = None


class ProductCategoryResponse(ProductCategoryBase):
    id: UUID
    company_id: UUID

    model_config = ConfigDict(from_attributes=True)


class ProductBase(BaseModel):
    category_id: Optional[UUID] = None
    sku: str = Field(..., max_length=100)
    name: str = Field(..., max_length=255)
    description: Optional[str] = None
    price: Decimal = Field(default=Decimal("0.00"), ge=0, max_digits=10, decimal_places=2)
    cost: Decimal = Field(default=Decimal("0.00"), ge=0, max_digits=10, decimal_places=2)
    unit_of_measure: str = Field(default="pcs", max_length=50)
    min_stock_level: Decimal = Field(default=Decimal("0.00"), ge=0, max_digits=10, decimal_places=2)
    is_active: bool = True


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    category_id: Optional[UUID] = None
    sku: Optional[str] = Field(None, max_length=100)
    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    price: Optional[Decimal] = Field(None, ge=0, max_digits=10, decimal_places=2)
    cost: Optional[Decimal] = Field(None, ge=0, max_digits=10, decimal_places=2)
    unit_of_measure: Optional[str] = Field(None, max_length=50)
    min_stock_level: Optional[Decimal] = Field(None, ge=0, max_digits=10, decimal_places=2)
    is_active: Optional[bool] = None


class ProductResponse(ProductBase):
    id: UUID
    company_id: UUID
    category: Optional[ProductCategoryResponse] = None

    model_config = ConfigDict(from_attributes=True)
