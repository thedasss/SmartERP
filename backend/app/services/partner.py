from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.models.partner import Supplier, Customer
from app.repositories.partner import SupplierRepository, CustomerRepository
from app.schemas.partner import (
    SupplierCreate, SupplierUpdate,
    CustomerCreate, CustomerUpdate
)


class PartnerService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.supplier_repo = SupplierRepository(session)
        self.customer_repo = CustomerRepository(session)

    # --- Suppliers ---

    async def get_suppliers(
        self, company_id: str, offset: int = 0, limit: int = 50
    ) -> tuple[List[Supplier], int]:
        return await self.supplier_repo.get_all(
            filters={"company_id": company_id}, offset=offset, limit=limit
        )

    async def get_supplier(self, supplier_id: str, company_id: str) -> Supplier:
        supplier = await self.supplier_repo.get_by_id(supplier_id)
        if not supplier or str(supplier.company_id) != str(company_id) or supplier.is_deleted:
            raise NotFoundError("Supplier not found")
        return supplier

    async def create_supplier(self, data: SupplierCreate, company_id: str) -> Supplier:
        return await self.supplier_repo.create(
            **data.model_dump(), company_id=company_id
        )

    async def update_supplier(
        self, supplier_id: str, data: SupplierUpdate, company_id: str
    ) -> Supplier:
        supplier = await self.get_supplier(supplier_id, company_id)
        return await self.supplier_repo.update(supplier, **data.model_dump(exclude_unset=True))

    async def delete_supplier(self, supplier_id: str, company_id: str) -> None:
        supplier = await self.get_supplier(supplier_id, company_id)
        await self.supplier_repo.soft_delete(supplier)

    # --- Customers ---

    async def get_customers(
        self, company_id: str, offset: int = 0, limit: int = 50
    ) -> tuple[List[Customer], int]:
        return await self.customer_repo.get_all(
            filters={"company_id": company_id}, offset=offset, limit=limit
        )

    async def get_customer(self, customer_id: str, company_id: str) -> Customer:
        customer = await self.customer_repo.get_by_id(customer_id)
        if not customer or str(customer.company_id) != str(company_id) or customer.is_deleted:
            raise NotFoundError("Customer not found")
        return customer

    async def create_customer(self, data: CustomerCreate, company_id: str) -> Customer:
        return await self.customer_repo.create(
            **data.model_dump(), company_id=company_id
        )

    async def update_customer(
        self, customer_id: str, data: CustomerUpdate, company_id: str
    ) -> Customer:
        customer = await self.get_customer(customer_id, company_id)
        return await self.customer_repo.update(customer, **data.model_dump(exclude_unset=True))

    async def delete_customer(self, customer_id: str, company_id: str) -> None:
        customer = await self.get_customer(customer_id, company_id)
        await self.customer_repo.soft_delete(customer)
