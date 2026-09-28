import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_procurement_to_inventory_flow(client: AsyncClient, token_headers: dict):
    # 1. Setup Data: Supplier, Category, Product, Warehouse
    # Supplier
    sup_response = await client.post("/api/v1/partners/suppliers", headers=token_headers, json={"name": "Test Supplier Corp"})
    supplier_id = sup_response.json()["id"]

    # Category & Product
    cat_response = await client.post("/api/v1/products/categories", headers=token_headers, json={"name": "Procurement Test Cat"})
    cat_id = cat_response.json()["id"]
    prod_response = await client.post(
        "/api/v1/products", headers=token_headers, 
        json={"category_id": cat_id, "sku": "PROC-001", "name": "Proc Product", "price": "100.00", "cost": "80.00"}
    )
    product_id = prod_response.json()["id"]

    # Warehouse
    wh_response = await client.post("/api/v1/inventory/warehouses", headers=token_headers, json={"name": "Proc WH", "code": "WH-PROC"})
    warehouse_id = wh_response.json()["id"]

    # 2. Create Purchase Order
    po_response = await client.post(
        "/api/v1/procurement/orders",
        headers=token_headers,
        json={
            "supplier_id": supplier_id,
            "notes": "Testing PO flow",
            "items": [
                {
                    "product_id": product_id,
                    "quantity": 100.00,
                    "unit_price": 80.00
                }
            ]
        }
    )
    assert po_response.status_code == 201
    po_data = po_response.json()
    po_id = po_data["id"]
    po_item_id = po_data["items"][0]["id"]
    assert po_data["status"] == "ISSUED"
    assert float(po_data["total_amount"]) == 8000.00

    # 3. Receive Partial Goods against PO
    gr_response = await client.post(
        f"/api/v1/procurement/orders/{po_id}/receive",
        headers=token_headers,
        json={
            "po_id": po_id,
            "warehouse_id": warehouse_id,
            "items": [
                {
                    "po_item_id": po_item_id,
                    "quantity_received": 40.00
                }
            ]
        }
    )
    assert gr_response.status_code == 201

    # 4. Verify PO is PARTIALLY_RECEIVED
    po_check = await client.get("/api/v1/procurement/orders", headers=token_headers)
    orders = po_check.json()
    po_updated = next(o for o in orders if o["id"] == po_id)
    assert po_updated["status"] == "PARTIALLY_RECEIVED"
    assert float(po_updated["items"][0]["received_quantity"]) == 40.0

    # 5. Verify Inventory Increased by 40
    stock_response = await client.get(
        f"/api/v1/inventory/stock?warehouse_id={warehouse_id}&product_id={product_id}",
        headers=token_headers
    )
    stock_data = stock_response.json()
    assert len(stock_data) == 1
    assert float(stock_data[0]["quantity"]) == 40.0

    # 6. Receive the rest of the goods (60)
    gr_response2 = await client.post(
        f"/api/v1/procurement/orders/{po_id}/receive",
        headers=token_headers,
        json={
            "po_id": po_id,
            "warehouse_id": warehouse_id,
            "items": [{"po_item_id": po_item_id, "quantity_received": 60.00}]
        }
    )
    assert gr_response2.status_code == 201

    # 7. Verify PO is RECEIVED
    po_check2 = await client.get("/api/v1/procurement/orders", headers=token_headers)
    orders2 = po_check2.json()
    po_updated2 = next(o for o in orders2 if o["id"] == po_id)
    assert po_updated2["status"] == "RECEIVED"

    # 8. Verify Inventory is now 100
    stock_response2 = await client.get(
        f"/api/v1/inventory/stock?warehouse_id={warehouse_id}&product_id={product_id}",
        headers=token_headers
    )
    assert float(stock_response2.json()[0]["quantity"]) == 100.0

    # 9. Verify Over-Receiving is Prevented
    gr_response3 = await client.post(
        f"/api/v1/procurement/orders/{po_id}/receive",
        headers=token_headers,
        json={
            "po_id": po_id,
            "warehouse_id": warehouse_id,
            "items": [{"po_item_id": po_item_id, "quantity_received": 1.00}]
        }
    )
    assert gr_response3.status_code == 400
    assert "Cannot receive goods for PO in status" in gr_response3.text
