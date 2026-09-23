from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text, case

from app.models.sales import SalesOrder, SOStatus
from app.models.inventory import StockItem
from app.models.product import Product, ProductCategory
from app.models.finance import Payment, Invoice, InvoiceType

class ReportService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_sales_trend(self, company_id: str):
        """
        Group sales orders by date.
        Note: For SQLite, we cast datetime to date using func.date().
        """
        stmt = (
            select(
                func.date(SalesOrder.created_at).label("sales_date"),
                func.sum(SalesOrder.total_amount).label("total_sales")
            )
            .where(
                SalesOrder.company_id == company_id,
                SalesOrder.status != SOStatus.CANCELLED
            )
            .group_by(func.date(SalesOrder.created_at))
            .order_by(func.date(SalesOrder.created_at))
        )
        
        result = await self.session.execute(stmt)
        data = []
        for row in result.all():
            data.append({
                "date": str(row.sales_date),
                "total_sales": row.total_sales or 0
            })
        return data

    async def get_inventory_valuation(self, company_id: str):
        """
        Group inventory value (qty * cost) by product category.
        """
        stmt = (
            select(
                ProductCategory.name.label("category_name"),
                func.sum(StockItem.quantity * Product.cost).label("total_value")
            )
            .select_from(StockItem)
            .join(Product, StockItem.product_id == Product.id)
            .join(ProductCategory, Product.category_id == ProductCategory.id)
            .where(StockItem.company_id == company_id)
            .group_by(ProductCategory.name)
        )
        
        result = await self.session.execute(stmt)
        data = []
        for row in result.all():
            data.append({
                "category_name": row.category_name,
                "total_value": row.total_value or 0
            })
        return data

    async def get_cash_flow(self, company_id: str):
        """
        Group payments by date, separating IN (Receivable) and OUT (Payable).
        """
        stmt = (
            select(
                Payment.payment_date.label("pay_date"),
                func.sum(
                    case(
                        (Invoice.type == InvoiceType.RECEIVABLE, Payment.amount),
                        else_=0
                    )
                ).label("money_in"),
                func.sum(
                    case(
                        (Invoice.type == InvoiceType.PAYABLE, Payment.amount),
                        else_=0
                    )
                ).label("money_out")
            )
            .select_from(Payment)
            .join(Invoice, Payment.invoice_id == Invoice.id)
            .where(Invoice.company_id == company_id)
            .group_by(Payment.payment_date)
            .order_by(Payment.payment_date)
        )
        
        result = await self.session.execute(stmt)
        data = []
        for row in result.all():
            data.append({
                "date": str(row.pay_date),
                "money_in": row.money_in or 0,
                "money_out": row.money_out or 0
            })
        return data
