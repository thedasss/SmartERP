import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_sales_to_inventory_flow(client: AsyncClient, token_headers: dict):
    # 1. Setup Data: Customer, Category, Product, Warehouse
    cust_response = await client.post("/api/v1/partners/customers", headers=token_headers, json={"name": "Test Customer Corp"})
    customer_id = cust_response.json()["id"]

    cat_response = await client.post("/api/v1/products/categories", headers=token_headers, json={"name": "Sales Test Cat"})
    cat_id = cat_response.json()["id"]
    
    prod_response = await client.post(
        "/api/v1/products", headers=token_headers, 
        json={"category_id": cat_id, "sku": "SALES-001", "name": "Sales Product", "price": "150.00", "cost": "80.00"}
    )
    product_id = prod_response.json()["id"]

    wh_response = await client.post("/api/v1/inventory/warehouses", headers=token_headers, json={"name": "Sales WH", "code": "WH-SALES"})
    warehouse_id = wh_response.json()["id"]

    # 2. Add Stock manually first (so we can ship it)
    stock_response = await client.post(
        "/api/v1/inventory/movements",
        headers=token_headers,
        json={
            "product_id": product_id,
            "warehouse_id": warehouse_id,
            "movement_type": "IN",
            "quantity": 100.00,
            "reference": "Initial Stock",
            "notes": "Testing"
        }
    )
    assert stock_response.status_code == 201

    # 3. Create Sales Order
    so_response = await client.post(
        "/api/v1/sales/orders",
        headers=token_headers,
        json={
            "customer_id": customer_id,
            "notes": "Testing SO flow",
            "items": [
                {
                    "product_id": product_id,
                    "quantity": 60.00,
                    "unit_price": 150.00
                }
            ]
        }
    )
    assert so_response.status_code == 201
    so_data = so_response.json()
    so_id = so_data["id"]
    so_item_id = so_data["items"][0]["id"]
    assert so_data["status"] == "CONFIRMED"
    assert float(so_data["total_amount"]) == 9000.00

    # 4. Ship Partial Goods against SO
    ship_response = await client.post(
        f"/api/v1/sales/orders/{so_id}/ship",
        headers=token_headers,
        json={
            "so_id": so_id,
            "warehouse_id": warehouse_id,
            "items": [
                {
                    "so_item_id": so_item_id,
                    "quantity_shipped": 40.00
                }
            ]
        }
    )
    assert ship_response.status_code == 201

    # 5. Verify SO is PARTIALLY_SHIPPED
    so_check = await client.get("/api/v1/sales/orders", headers=token_headers)
    orders = so_check.json()
    so_updated = next(o for o in orders if o["id"] == so_id)
    assert so_updated["status"] == "PARTIALLY_SHIPPED"
    assert float(so_updated["items"][0]["shipped_quantity"]) == 40.0

    # 6. Verify Inventory Decreased (Started with 100, shipped 40, expect 60)
    stock_check = await client.get(
        f"/api/v1/inventory/stock?warehouse_id={warehouse_id}&product_id={product_id}",
        headers=token_headers
    )
    stock_data = stock_check.json()
    assert float(stock_data[0]["quantity"]) == 60.0

    # 7. Attempt to Over-Ship (remaining order qty is 20, we try to ship 30)
    ship_response_over = await client.post(
        f"/api/v1/sales/orders/{so_id}/ship",
        headers=token_headers,
        json={
            "so_id": so_id,
            "warehouse_id": warehouse_id,
            "items": [{"so_item_id": so_item_id, "quantity_shipped": 30.00}]
        }
    )
    assert ship_response_over.status_code == 400

    # 8. Attempt to ship remaining (20) which should succeed
    ship_response2 = await client.post(
        f"/api/v1/sales/orders/{so_id}/ship",
        headers=token_headers,
        json={
            "so_id": so_id,
            "warehouse_id": warehouse_id,
            "items": [{"so_item_id": so_item_id, "quantity_shipped": 20.00}]
        }
    )
    assert ship_response2.status_code == 201

    # 9. Verify SO is SHIPPED
    so_check2 = await client.get("/api/v1/sales/orders", headers=token_headers)
    orders2 = so_check2.json()
    so_updated2 = next(o for o in orders2 if o["id"] == so_id)
    assert so_updated2["status"] == "SHIPPED"

    # 10. Verify Inventory is now 40
    stock_check2 = await client.get(
        f"/api/v1/inventory/stock?warehouse_id={warehouse_id}&product_id={product_id}",
        headers=token_headers
    )
    assert float(stock_check2.json()[0]["quantity"]) == 40.0
