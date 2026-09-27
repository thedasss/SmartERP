import asyncio
import uuid
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import AsyncSessionLocal
from app.models.company import Company
from app.models.user import User
from app.models.product import ProductCategory, Product
from app.models.inventory import Warehouse, StockItem, StockMovement, MovementType
from sqlalchemy import select

async def seed():
    async with AsyncSessionLocal() as session:
        # Get the first company
        result = await session.execute(select(Company))
        company = result.scalar()
        if not company:
            print("No company found! Run the system once to create the default admin/company.")
            return

        company_id = str(company.id)

        # 1. Create a Category
        cat = ProductCategory(
            company_id=company_id,
            name="Electronics",
            description="Electronic items and gadgets"
        )
        session.add(cat)
        await session.flush()

        # 2. Create Products
        prod1 = Product(
            company_id=company_id,
            category_id=str(cat.id),
            sku="LAP-001",
            name="ProBook Laptop",
            price=Decimal("1200.00"),
            cost=Decimal("950.00"),
            unit_of_measure="pcs"
        )
        prod2 = Product(
            company_id=company_id,
            category_id=str(cat.id),
            sku="MOU-001",
            name="Wireless Mouse",
            price=Decimal("45.00"),
            cost=Decimal("15.00"),
            unit_of_measure="pcs"
        )
        session.add_all([prod1, prod2])
        await session.flush()

        # 3. Create a Warehouse
        wh = Warehouse(
            company_id=company_id,
            name="Central Hub",
            code="WH-CENTRAL",
            location="New York"
        )
        session.add(wh)
        await session.flush()

        # 4. Create Stock Items
        si1 = StockItem(
            company_id=company_id,
            warehouse_id=str(wh.id),
            product_id=str(prod1.id),
            quantity=Decimal("50.00")
        )
        si2 = StockItem(
            company_id=company_id,
            warehouse_id=str(wh.id),
            product_id=str(prod2.id),
            quantity=Decimal("150.00")
        )
        session.add_all([si1, si2])
        await session.flush()

        # 5. Create Movement Logs
        mov1 = StockMovement(
            company_id=company_id,
            product_id=str(prod1.id),
            warehouse_id=str(wh.id),
            movement_type=MovementType.IN,
            quantity=Decimal("50.00"),
            reference="Initial Seed",
        )
        mov2 = StockMovement(
            company_id=company_id,
            product_id=str(prod2.id),
            warehouse_id=str(wh.id),
            movement_type=MovementType.IN,
            quantity=Decimal("150.00"),
            reference="Initial Seed",
        )
        session.add_all([mov1, mov2])
        
        await session.commit()
        print("Database seeded successfully with dummy inventory data!")

if __name__ == "__main__":
    asyncio.run(seed())
