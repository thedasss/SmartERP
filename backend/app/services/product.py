from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, NotFoundError
from app.models.product import Product, ProductCategory
from app.repositories.product import ProductRepository, ProductCategoryRepository
from app.schemas.product import (
    ProductCreate, ProductUpdate, 
    ProductCategoryCreate, ProductCategoryUpdate
)


class ProductService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.product_repo = ProductRepository(session)
        self.category_repo = ProductCategoryRepository(session)

    # --- Categories ---

    async def get_categories(
        self, company_id: str, offset: int = 0, limit: int = 50
    ) -> tuple[List[ProductCategory], int]:
        return await self.category_repo.get_all(
            filters={"company_id": company_id}, offset=offset, limit=limit
        )

    async def get_category(self, category_id: str, company_id: str) -> ProductCategory:
        category = await self.category_repo.get_by_id(category_id)
        if not category or str(category.company_id) != str(company_id) or category.is_deleted:
            raise NotFoundError("Category not found")
        return category

    async def create_category(
        self, data: ProductCategoryCreate, company_id: str
    ) -> ProductCategory:
        return await self.category_repo.create(
            **data.model_dump(), company_id=company_id
        )

    async def update_category(
        self, category_id: str, data: ProductCategoryUpdate, company_id: str
    ) -> ProductCategory:
        category = await self.get_category(category_id, company_id)
        return await self.category_repo.update(category, **data.model_dump(exclude_unset=True))

    async def delete_category(self, category_id: str, company_id: str) -> None:
        category = await self.get_category(category_id, company_id)
        # Check if products exist in category before deleting
        products, total = await self.product_repo.get_all({"category_id": category_id, "company_id": company_id})
        if total > 0:
            raise ConflictError("Cannot delete category with associated products.")
        await self.category_repo.soft_delete(category)


    # --- Products ---

    async def get_products(
        self, company_id: str, offset: int = 0, limit: int = 50
    ) -> tuple[List[Product], int]:
        return await self.product_repo.get_all(
            filters={"company_id": company_id}, offset=offset, limit=limit
        )

    async def get_product(self, product_id: str, company_id: str) -> Product:
        product = await self.product_repo.get_by_id(product_id)
        if not product or str(product.company_id) != str(company_id) or product.is_deleted:
            raise NotFoundError("Product not found")
        return product

    async def create_product(self, data: ProductCreate, company_id: str) -> Product:
        existing = await self.product_repo.get_by_sku(company_id, data.sku)
        if existing:
            raise ConflictError(f"Product with SKU '{data.sku}' already exists.")
        
        category = None
        if data.category_id:
            # Validate category exists
            category = await self.get_category(str(data.category_id), company_id)

        create_data = data.model_dump()
        if create_data.get("category_id"):
            create_data["category_id"] = str(create_data["category_id"])

        product = await self.product_repo.create(
            **create_data, company_id=company_id
        )
        if category:
            product.category = category
        return product

    async def update_product(
        self, product_id: str, data: ProductUpdate, company_id: str
    ) -> Product:
        product = await self.get_product(product_id, company_id)
        
        if data.sku and data.sku != product.sku:
            existing = await self.product_repo.get_by_sku(company_id, data.sku)
            if existing:
                raise ConflictError(f"Product with SKU '{data.sku}' already exists.")

        category = None
        if data.category_id:
            category = await self.get_category(str(data.category_id), company_id)

        update_data = data.model_dump(exclude_unset=True)
        if "category_id" in update_data and update_data["category_id"]:
            update_data["category_id"] = str(update_data["category_id"])

        product = await self.product_repo.update(product, **update_data)
        if category:
            product.category = category
        return product

    async def delete_product(self, product_id: str, company_id: str) -> None:
        product = await self.get_product(product_id, company_id)
        await self.product_repo.soft_delete(product)
