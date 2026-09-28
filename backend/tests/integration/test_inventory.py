import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_warehouse(client: AsyncClient, token_headers: dict):
    response = await client.post(
        "/api/v1/inventory/warehouses",
        headers=token_headers,
        json={
            "name": "Main Warehouse",
            "code": "WH-MAIN",
            "location": "New York"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Main Warehouse"
    assert data["code"] == "WH-MAIN"
    assert "id" in data

@pytest.mark.asyncio
async def test_list_warehouses(client: AsyncClient, token_headers: dict):
    # Ensure warehouse exists
    await client.post(
        "/api/v1/inventory/warehouses",
        headers=token_headers,
        json={"name": "Second WH", "code": "WH-2", "location": "LA"}
    )
    
    response = await client.get("/api/v1/inventory/warehouses", headers=token_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1

@pytest.mark.asyncio
async def test_record_movement(client: AsyncClient, token_headers: dict):
    # 1. Create a category
    cat_response = await client.post(
        "/api/v1/products/categories",
        headers=token_headers,
        json={"name": "Inventory Test Category"}
    )
    cat_id = cat_response.json()["id"]

    # 2. Create a product
    prod_response = await client.post(
        "/api/v1/products",
        headers=token_headers,
        json={
            "category_id": cat_id,
            "sku": "INV-001",
            "name": "Inventory Test Product",
            "price": "10.00",
            "cost": "5.00"
        }
    )
    product_id = prod_response.json()["id"]

    # 3. Create a warehouse
    wh_response = await client.post(
        "/api/v1/inventory/warehouses",
        headers=token_headers,
        json={"name": "WH for Movement", "code": "WH-MOV"}
    )
    warehouse_id = wh_response.json()["id"]

    # 4. Record stock movement (IN)
    mov_response = await client.post(
        "/api/v1/inventory/movements",
        headers=token_headers,
        json={
            "product_id": product_id,
            "warehouse_id": warehouse_id,
            "movement_type": "IN",
            "quantity": 50.00,
            "reference": "PO-12345"
        }
    )
    assert mov_response.status_code == 201
    mov_data = mov_response.json()
    assert mov_data["movement_type"] == "IN"
    assert float(mov_data["quantity"]) == 50.0

    # 5. Check stock level
    stock_response = await client.get(
        f"/api/v1/inventory/stock?warehouse_id={warehouse_id}&product_id={product_id}",
        headers=token_headers
    )
    assert stock_response.status_code == 200
    stock_data = stock_response.json()
    assert len(stock_data) == 1
    assert float(stock_data[0]["quantity"]) == 50.0

    # 6. Record stock movement (OUT)
    out_response = await client.post(
        "/api/v1/inventory/movements",
        headers=token_headers,
        json={
            "product_id": product_id,
            "warehouse_id": warehouse_id,
            "movement_type": "OUT",
            "quantity": 10.00,
            "reference": "INV-12345"
        }
    )
    assert out_response.status_code == 201

    # 7. Check stock level again (should be 40)
    stock_response2 = await client.get(
        f"/api/v1/inventory/stock?warehouse_id={warehouse_id}&product_id={product_id}",
        headers=token_headers
    )
    stock_data2 = stock_response2.json()
    assert float(stock_data2[0]["quantity"]) == 40.0

@pytest.mark.asyncio
async def test_negative_stock_prevention(client: AsyncClient, token_headers: dict):
    # 1. Create a product and warehouse
    cat_response = await client.post("/api/v1/products/categories", headers=token_headers, json={"name": "Cat2"})
    prod_response = await client.post("/api/v1/products", headers=token_headers, json={"category_id": cat_response.json()["id"], "sku": "INV-002", "name": "Prod2"})
    wh_response = await client.post("/api/v1/inventory/warehouses", headers=token_headers, json={"name": "WH2", "code": "WH-NEG"})
    
    product_id = prod_response.json()["id"]
    warehouse_id = wh_response.json()["id"]

    # 2. Try to move OUT without any IN
    mov_response = await client.post(
        "/api/v1/inventory/movements",
        headers=token_headers,
        json={
            "product_id": product_id,
            "warehouse_id": warehouse_id,
            "movement_type": "OUT",
            "quantity": 10.00
        }
    )
    assert mov_response.status_code == 422
    assert "Insufficient stock" in mov_response.text
