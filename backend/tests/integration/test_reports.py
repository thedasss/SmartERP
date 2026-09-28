import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_reports(client: AsyncClient, token_headers: dict):
    # Just verify that the endpoints return 200 and the correct structure
    # In a full test suite, we'd seed data and assert exact sums.
    
    # 1. Sales Trend
    sales_resp = await client.get("/api/v1/reports/sales/trend", headers=token_headers)
    assert sales_resp.status_code == 200
    assert "data" in sales_resp.json()
    
    # 2. Inventory Valuation
    inv_resp = await client.get("/api/v1/reports/inventory/valuation", headers=token_headers)
    assert inv_resp.status_code == 200
    assert "data" in inv_resp.json()
    
    # 3. Cash Flow
    cash_resp = await client.get("/api/v1/reports/finance/cashflow", headers=token_headers)
    assert cash_resp.status_code == 200
    assert "data" in cash_resp.json()
