from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.partner import Supplier, Customer
from app.repositories.base import BaseRepository


class SupplierRepository(BaseRepository[Supplier]):
    def __init__(self, session: AsyncSession):
        super().__init__(Supplier, session)


class CustomerRepository(BaseRepository[Customer]):
    def __init__(self, session: AsyncSession):
        super().__init__(Customer, session)
