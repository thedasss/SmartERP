"""
API v1 router — aggregates all route modules.
"""
from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.users import router as users_router
from app.api.v1.products import router as products_router
from app.api.v1.partners import router as partners_router
from app.api.v1.inventory import router as inventory_router
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.procurement import router as procurement_router
from app.api.v1.sales import router as sales_router
from app.api.v1.finance import router as finance_router
from app.api.v1.reports import router as reports_router
from app.api.v1.documents import router as documents_router
from app.api.v1.ai import router as ai_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(dashboard_router, prefix="/dashboard", tags=["Dashboard"])
api_router.include_router(products_router, prefix="/products", tags=["Products"])
api_router.include_router(partners_router, prefix="/partners", tags=["Partners"])
api_router.include_router(inventory_router, prefix="/inventory", tags=["Inventory"])
api_router.include_router(procurement_router, prefix="/procurement", tags=["Procurement"])
api_router.include_router(sales_router, prefix="/sales", tags=["Sales"])
api_router.include_router(finance_router, prefix="/finance", tags=["Finance"])
api_router.include_router(reports_router, prefix="/reports", tags=["Reports"])
api_router.include_router(documents_router, prefix="/documents", tags=["Documents"])
api_router.include_router(ai_router, prefix="/ai", tags=["AI"])
