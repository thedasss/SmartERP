"""
SmartERP FastAPI Application — main entry point.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.exceptions import SmartERPException
from app.core.logging import get_logger, setup_logging
from app.core.redis import close_redis

settings = get_settings()
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events."""
    logger.info(
        "SmartERP starting",
        env=settings.app_env,
        version=settings.app_version,
    )
    yield
    logger.info("SmartERP shutting down")
    await close_redis()


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI-Powered Procurement, Inventory & Document Management ERP",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# ── CORS ─────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Global Exception Handlers ─────────────────────────────────


@app.exception_handler(SmartERPException)
async def smarterp_exception_handler(
    request: Request, exc: SmartERPException
) -> JSONResponse:
    logger.warning(
        "Business exception",
        error_code=exc.error_code,
        message=exc.message,
        path=str(request.url),
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.message,
            "error_code": exc.error_code,
            "details": exc.details,
        },
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception(
        "Unhandled exception",
        path=str(request.url),
        exc_type=type(exc).__name__,
    )
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "An internal server error occurred. Please try again later.",
            "error_code": "INTERNAL_SERVER_ERROR",
        },
    )


# ── Routes ────────────────────────────────────────────────────

app.include_router(api_router)


@app.get("/api/v1/health", tags=["Health"])
async def health_check():
    """Health check endpoint — verifies database connectivity."""
    from sqlalchemy import text
    from app.core.database import AsyncSessionLocal

    db_ok = False
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
            db_ok = True
    except Exception as e:
        logger.error("Database health check failed", error=str(e))

    status = "healthy" if db_ok else "degraded"
    return {
        "status": status,
        "version": settings.app_version,
        "database": "connected" if db_ok else "error",
        "environment": settings.app_env,
    }


@app.get("/", include_in_schema=False)
async def root():
    return {"message": f"Welcome to {settings.app_name} API", "docs": "/docs"}
