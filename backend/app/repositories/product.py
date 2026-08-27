from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.product import Product, ProductCategory
from app.repositories.base import BaseRepository


class ProductCategoryRepository(BaseRepository[ProductCategory]):
    def __init__(self, session: AsyncSession):
        super().__init__(ProductCategory, session)


class ProductRepository(BaseRepository[Product]):
    def __init__(self, session: AsyncSession):
        super().__init__(Product, session)

    async def get_by_sku(self, company_id: str, sku: str) -> Product | None:
        result = await self.session.execute(
            select(Product)
            .where(Product.company_id == company_id, Product.sku == sku, Product.is_deleted.is_(False))
        )
        return result.scalar_one_or_none()
