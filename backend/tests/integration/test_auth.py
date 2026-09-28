"""
Authentication integration tests.
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.models.base import generate_uuid
from app.models.company import Company
from app.models.user import User


async def _seed_test_user(db: AsyncSession) -> tuple[Company, User]:
    """Create a test company and user for auth tests."""
    company = Company(
        id=generate_uuid(),
        name="Test Company",
        code="TEST001",
        email="test@example.com",
    )
    db.add(company)
    await db.flush()

    user = User(
        id=generate_uuid(),
        company_id=company.id,
        email="test@example.com",
        password_hash=hash_password("Test@12345"),
        first_name="Test",
        last_name="User",
        is_active=True,
        is_super_admin=True,
    )
    db.add(user)
    await db.flush()
    return company, user


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, db_session: AsyncSession):
    company, user = await _seed_test_user(db_session)
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "Test@12345"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient, db_session: AsyncSession):
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "WrongPassword"},
    )
    assert response.status_code == 401
    assert response.json()["success"] is False


@pytest.mark.asyncio
async def test_get_me_requires_auth(client: AsyncClient):
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_me_authenticated(client: AsyncClient, db_session: AsyncSession):
    # Login first
    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "Test@12345"},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    me_response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_response.status_code == 200
    me = me_response.json()
    assert me["email"] == "test@example.com"
    assert me["is_super_admin"] is True


@pytest.mark.asyncio
async def test_refresh_token(client: AsyncClient, db_session: AsyncSession):
    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "Test@12345"},
    )
    refresh_token = login_response.json()["refresh_token"]

    refresh_response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert refresh_response.status_code == 200
    assert "access_token" in refresh_response.json()


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] in ("healthy", "degraded")
