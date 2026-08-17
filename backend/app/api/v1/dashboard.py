from typing import Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.inventory import StockItem
from app.models.product import Product
from app.models.procurement import PurchaseOrder, POStatus

router = APIRouter()

@router.get("/stats")
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get aggregated statistics for the dashboard.
    """
    company_id = str(current_user.company_id)
    
    # Calculate Total Inventory Value
    stmt_inv = (
        select(
            func.sum(StockItem.quantity * Product.cost).label("total_value"),
            func.count(StockItem.id).label("total_items")
        )
        .join(Product, StockItem.product_id == Product.id)
        .where(StockItem.company_id == company_id)
    )
    
    result_inv = await db.execute(stmt_inv)
    row_inv = result_inv.one_or_none()
    
    total_inventory_value = float(row_inv.total_value) if row_inv and row_inv.total_value else 0.0
    total_inventory_items = int(row_inv.total_items) if row_inv and row_inv.total_items else 0
    
    # Calculate Total Purchases (Sum of non-cancelled POs)
    stmt_po = (
        select(func.sum(PurchaseOrder.total_amount).label("total_purchases"))
        .where(
            PurchaseOrder.company_id == company_id,
            PurchaseOrder.status != POStatus.CANCELLED
        )
    )
    result_po = await db.execute(stmt_po)
    row_po = result_po.one_or_none()
    total_purchases = float(row_po.total_purchases) if row_po and row_po.total_purchases else 0.0

    # Calculate Total Sales (Sum of non-cancelled SOs)
    from app.models.sales import SalesOrder, SOStatus
    stmt_so = (
        select(func.sum(SalesOrder.total_amount).label("total_sales"))
        .where(
            SalesOrder.company_id == company_id,
            SalesOrder.status != SOStatus.CANCELLED
        )
    )
    result_so = await db.execute(stmt_so)
    row_so = result_so.one_or_none()
    total_sales = float(row_so.total_sales) if row_so and row_so.total_sales else 0.0

    # Calculate Outstanding Invoices (Count of non-paid, non-cancelled invoices)
    from app.models.finance import Invoice, InvoiceStatus
    stmt_inv_count = (
        select(func.count(Invoice.id).label("outstanding_count"))
        .where(
            Invoice.company_id == company_id,
            Invoice.status.in_([InvoiceStatus.ISSUED, InvoiceStatus.PARTIALLY_PAID])
        )
    )
    result_inv_count = await db.execute(stmt_inv_count)
    row_inv_count = result_inv_count.one_or_none()
    outstanding_invoices = int(row_inv_count.outstanding_count) if row_inv_count and row_inv_count.outstanding_count else 0

    # Fetch recent activities
    activities = []
    
    # 1. Recent Sales Orders
    stmt_recent_so = select(SalesOrder).where(SalesOrder.company_id == company_id).order_by(SalesOrder.created_at.desc()).limit(3)
    recent_sos = (await db.execute(stmt_recent_so)).unique().scalars().all()
    for so in recent_sos:
        activities.append({
            "id": f"so-{so.id}",
            "type": "sale",
            "description": f"New Sales Order {so.so_number} created",
            "amount": float(so.total_amount),
            "timestamp": so.created_at.isoformat() if so.created_at else ""
        })

    # 2. Recent Purchase Orders
    stmt_recent_po = select(PurchaseOrder).where(PurchaseOrder.company_id == company_id).order_by(PurchaseOrder.created_at.desc()).limit(3)
    recent_pos = (await db.execute(stmt_recent_po)).unique().scalars().all()
    for po in recent_pos:
        activities.append({
            "id": f"po-{po.id}",
            "type": "purchase",
            "description": f"Purchase Order {po.po_number} created",
            "amount": float(po.total_amount),
            "timestamp": po.created_at.isoformat() if po.created_at else ""
        })
        
    # 3. Recent Invoices
    stmt_recent_inv = select(Invoice).where(Invoice.company_id == company_id).order_by(Invoice.created_at.desc()).limit(3)
    recent_invs = (await db.execute(stmt_recent_inv)).unique().scalars().all()
    for inv in recent_invs:
        activities.append({
            "id": f"inv-{inv.id}",
            "type": "invoice",
            "description": f"Invoice {inv.invoice_number} generated",
            "amount": float(inv.total_amount),
            "timestamp": inv.created_at.isoformat() if inv.created_at else ""
        })

    # Sort all activities by timestamp descending and take top 5
    activities.sort(key=lambda x: x["timestamp"], reverse=True)
    recent_activities = activities[:5]

    return {
        "sales": {
            "total": total_sales,
            "change": "active"
        },
        "purchases": {
            "total": total_purchases,
            "change": "active"
        },
        "invoices": {
            "outstanding": outstanding_invoices,
            "change": f"{outstanding_invoices} pending"
        },
        "inventory": {
            "value": total_inventory_value,
            "items_count": total_inventory_items
        },
        "recent_activities": recent_activities
    }
