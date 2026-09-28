import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_category(client: AsyncClient, token_headers: dict):
    response = await client.post(
        "/api/v1/products/categories",
        headers=token_headers,
        json={"name": "Electronics", "description": "Electronic items"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Electronics"
    assert "id" in data


@pytest.mark.asyncio
async def test_create_product(client: AsyncClient, token_headers: dict):
    # Create category first
    cat_response = await client.post(
        "/api/v1/products/categories",
        headers=token_headers,
        json={"name": "Office Supplies"},
    )
    cat_id = cat_response.json()["id"]

    # Create product
    response = await client.post(
        "/api/v1/products",
        headers=token_headers,
        json={
            "category_id": cat_id,
            "sku": "OFF-001",
            "name": "A4 Paper",
            "price": "5.99",
            "cost": "2.50",
            "unit_of_measure": "ream",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["sku"] == "OFF-001"
    assert data["price"] == "5.99"


@pytest.mark.asyncio
async def test_create_supplier(client: AsyncClient, token_headers: dict):
    response = await client.post(
        "/api/v1/partners/suppliers",
        headers=token_headers,
        json={
            "name": "Global Tech Supplies",
            "contact_name": "Jane Doe",
            "email": "jane@globaltech.com"
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Global Tech Supplies"
    assert data["email"] == "jane@globaltech.com"


@pytest.mark.asyncio
async def test_create_customer(client: AsyncClient, token_headers: dict):
    response = await client.post(
        "/api/v1/partners/customers",
        headers=token_headers,
        json={
            "name": "Acme Corp",
            "contact_name": "John Smith",
            "email": "john@acme.com"
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Acme Corp"
    assert data["email"] == "john@acme.com"
