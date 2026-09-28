from app.core.security import create_access_token
from app.models.base import generate_uuid
from app.models.company import Company
from app.models.user import User
from app.core.security import hash_password

@pytest_asyncio.fixture
async def token_headers(db_session: AsyncSession) -> dict:
    """Returns headers with a valid access token for a test user."""
    # Create test company and user
    company = Company(
        id=generate_uuid(),
        name="Fixture Company",
        code="FIX001",
        email="fixture@example.com",
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
    )
    db_session.add(user)
    await db_session.commit()

    token = create_access_token({"sub": user.id})
    return {"Authorization": f"Bearer {token}"}
