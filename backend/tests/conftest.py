"""
Test configuration and fixtures for SmartERP.
Uses an in-memory SQLite database for unit tests.
"""
import asyncio
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.database import Base, get_db
from app.main import app

# Use SQLite for tests (no MySQL needed)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def test_engine():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    session_factory = async_sessionmaker(test_engine, expire_on_commit=False)
    async with session_factory() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def client(db_session) -> AsyncGenerator[AsyncClient, None]:
    """HTTP test client with overridden DB dependency."""
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac
    app.dependency_overrides.clear()


from app.core.security import create_access_token, hash_password
from app.models.base import generate_uuid
from app.models.company import Company
from app.models.user import User

@pytest_asyncio.fixture
async def token_headers(db_session: AsyncSession) -> dict:
    """Returns headers with a valid access token for a test user."""
    # Create test company and user
    company = Company(
        id=generate_uuid(),
        name="Fixture Company",
        code=f"FIX-{generate_uuid()[:8]}",
        email=f"fixture-{generate_uuid()[:8]}@example.com",
    )
    db_session.add(company)
    await db_session.flush()

    user = User(
        id=generate_uuid(),
        company_id=company.id,
        email="fixtureuser@example.com",
        password_hash=hash_password("Test@12345"),
        first_name="Fixture",
        last_name="User",
        is_active=True,
        is_super_admin=True,
        is_deleted=False,
    )
    db_session.add(user)
    await db_session.flush()

    token = create_access_token(user.id)
    return {"Authorization": f"Bearer {token}"}
