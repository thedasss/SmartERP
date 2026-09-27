import asyncio
import sys
import os
import random
from datetime import datetime, timedelta, timezone

# Add the parent directory to sys.path so we can import from app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from faker import Faker
from app.core.database import AsyncSessionLocal
from app.models.company import Company
from app.models.user import User
from app.models.product import Product, ProductCategory
from app.models.partner import Customer, Supplier
from app.models.sales import SalesOrder, SalesOrderItem, SOStatus
from app.models.finance import Invoice, InvoiceStatus, InvoiceType
from app.models.inventory import Warehouse, StockItem
from app.core.security import hash_password

fake = Faker()

async def main():
    async with AsyncSessionLocal() as db:
        print("Creating mock data...")
        
        # 1. Ensure Company and Admin User exist
        stmt = select(Company).limit(1)
        result = await db.execute(stmt)
        company = result.scalar_one_or_none()
        
        if not company:
            company = Company(name="Acme Corp")
            db.add(company)
            await db.flush()
            print("Created company Acme Corp")
            
        stmt = select(User).where(User.company_id == company.id).limit(1)
        result = await db.execute(stmt)
        admin = result.scalar_one_or_none()
        
        if not admin:
            admin = User(
                company_id=company.id,
                email="admin@acmecorp.com",
                hashed_password=hash_password("password123"),
                first_name="Admin",
                last_name="User",
                role="ADMIN"
            )
            db.add(admin)
            await db.flush()
            print("Created admin user admin@acmecorp.com")
            
        # 2. Products
        # Create a default category
        category = ProductCategory(
            company_id=company.id,
            name="General Goods",
            description="General merchandise"
        )
        db.add(category)
        await db.flush()

        categories = ["Electronics", "Furniture", "Office Supplies", "Software", "Hardware"]
        products = []
        for i in range(20):
            cat_name = random.choice(categories)
            product = Product(
                company_id=company.id,
                category_id=category.id,
                name=f"{fake.word().capitalize()} {cat_name}",
                sku=f"SKU-{fake.ean(length=8)}",
                description=fake.sentence(),
                price=round(random.uniform(10.0, 500.0), 2),
                cost=round(random.uniform(5.0, 200.0), 2)
            )
            db.add(product)
            products.append(product)
        await db.flush()
        print(f"Created 20 products")
        
        # 3. Partners (Customers and Suppliers)
        customers = []
        for i in range(10):
            customer = Customer(
                company_id=company.id,
                name=fake.company(),
                email=fake.company_email(),
                phone=fake.phone_number(),
                address=fake.address()
            )
            db.add(customer)
            customers.append(customer)
            
        suppliers = []
        for i in range(5):
            supplier = Supplier(
                company_id=company.id,
                name=fake.company(),
                email=fake.company_email(),
                phone=fake.phone_number(),
                address=fake.address()
            )
            db.add(supplier)
            suppliers.append(supplier)
            
        await db.flush()
        print(f"Created 15 partners")

        # 4. Warehouses & Stock
        warehouse = Warehouse(
            company_id=company.id,
            name="Main Warehouse",
            code="WH-MAIN",
            location="New York"
        )
        db.add(warehouse)
        await db.flush()
        
        for p in products:
            stock = StockItem(
                company_id=company.id,
                warehouse_id=warehouse.id,
                product_id=p.id,
                quantity=random.randint(10, 500)
            )
            db.add(stock)
        print("Created warehouse and stock")

        # 5. Sales Orders & Invoices (Historical Data)
        if customers:
            now = datetime.now(timezone.utc)
            for i in range(40):
                # Spread orders over the last 6 months
                days_ago = random.randint(1, 180)
                order_date = now - timedelta(days=days_ago)
                
                customer = random.choice(customers)
                order = SalesOrder(
                    company_id=company.id,
                    customer_id=customer.id,
                    so_number=f"SO-{fake.ean(length=8)}",
                    status=SOStatus.SHIPPED,
                    total_amount=0
                )
                order.created_at = order_date
                db.add(order)
                await db.flush()
                
                total = 0
                # 1 to 5 items per order
                for _ in range(random.randint(1, 5)):
                    prod = random.choice(products)
                    qty = random.randint(1, 10)
                    item_total = prod.price * qty
                    total += item_total
                    
                    item = SalesOrderItem(
                        so_id=order.id,
                        product_id=prod.id,
                        quantity=qty,
                        unit_price=prod.price,
                    )
                    db.add(item)
                
                order.total_amount = total
                
                # Create corresponding Invoice
                inv_status = random.choice([InvoiceStatus.ISSUED, InvoiceStatus.PAID, InvoiceStatus.PAID])
                invoice = Invoice(
                    company_id=company.id,
                    partner_id=customer.id,
                    type=InvoiceType.RECEIVABLE,
                    invoice_number=f"INV-{fake.ean(length=8)}",
                    status=inv_status,
                    total_amount=total,
                    amount_paid=total if inv_status == InvoiceStatus.PAID else 0,
                    due_date=order_date + timedelta(days=30)
                )
                invoice.created_at = order_date
                db.add(invoice)
                
            print("Created 40 Sales Orders & Invoices")

        await db.commit()
        print("Successfully generated mock data!")

if __name__ == "__main__":
    asyncio.run(main())
