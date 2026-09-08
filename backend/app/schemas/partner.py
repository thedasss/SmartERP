from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class PartnerBase(BaseModel):
    name: str = Field(..., max_length=255)
    contact_name: Optional[str] = Field(None, max_length=255)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=50)
    address: Optional[str] = None
    tax_number: Optional[str] = Field(None, max_length=100)
    is_active: bool = True


class PartnerCreate(PartnerBase):
    pass


class PartnerUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    contact_name: Optional[str] = Field(None, max_length=255)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=50)
    address: Optional[str] = None
    tax_number: Optional[str] = Field(None, max_length=100)
    is_active: Optional[bool] = None


class PartnerResponse(PartnerBase):
    id: UUID
    company_id: UUID

    model_config = ConfigDict(from_attributes=True)


# For clarity, we define distinct types for Supplier and Customer
# even though they share the same schema structure currently.

class SupplierCreate(PartnerCreate):
    pass

class SupplierUpdate(PartnerUpdate):
    pass

class SupplierResponse(PartnerResponse):
    pass

class CustomerCreate(PartnerCreate):
    pass

class CustomerUpdate(PartnerUpdate):
    pass

class CustomerResponse(PartnerResponse):
    pass
