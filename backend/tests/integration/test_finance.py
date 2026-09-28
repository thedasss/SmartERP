import pytest
from httpx import AsyncClient
from datetime import date, timedelta

@pytest.mark.asyncio
async def test_finance_flow(client: AsyncClient, token_headers: dict):
    # 1. Setup Data: Customer
    cust_response = await client.post("/api/v1/partners/customers", headers=token_headers, json={"name": "Test Customer for Invoice"})
    customer_id = cust_response.json()["id"]

    # 2. Create Invoice
    due_date = (date.today() + timedelta(days=30)).isoformat()
    inv_response = await client.post(
        "/api/v1/finance/invoices",
        headers=token_headers,
        json={
            "partner_id": customer_id,
            "type": "RECEIVABLE",
            "total_amount": 5000.00,
            "due_date": due_date,
            "notes": "Test Invoice"
        }
    )
    assert inv_response.status_code == 201
    inv_data = inv_response.json()
    inv_id = inv_data["id"]
    assert inv_data["status"] == "ISSUED"
    assert float(inv_data["amount_paid"]) == 0.0

    # 3. Partial Payment
    payment_date = date.today().isoformat()
    pay1_response = await client.post(
        f"/api/v1/finance/invoices/{inv_id}/payments",
        headers=token_headers,
        json={
            "amount": 2000.00,
            "payment_date": payment_date,
            "reference_number": "TRX-001"
        }
    )
    assert pay1_response.status_code == 201

    # 4. Verify Invoice is PARTIALLY_PAID
    inv_check1 = await client.get("/api/v1/finance/invoices", headers=token_headers)
    invoices = inv_check1.json()
    inv_updated1 = next(i for i in invoices if i["id"] == inv_id)
    assert inv_updated1["status"] == "PARTIALLY_PAID"
    assert float(inv_updated1["amount_paid"]) == 2000.00

    # 5. Overpayment (Remaining is 3000, attempt 4000)
    pay_over_response = await client.post(
        f"/api/v1/finance/invoices/{inv_id}/payments",
        headers=token_headers,
        json={
            "amount": 4000.00,
            "payment_date": payment_date
        }
    )
    assert pay_over_response.status_code == 400

    # 6. Final Payment
    pay2_response = await client.post(
        f"/api/v1/finance/invoices/{inv_id}/payments",
        headers=token_headers,
        json={
            "amount": 3000.00,
            "payment_date": payment_date,
            "reference_number": "TRX-002"
        }
    )
    assert pay2_response.status_code == 201

    # 7. Verify Invoice is PAID
    inv_check2 = await client.get("/api/v1/finance/invoices", headers=token_headers)
    invoices2 = inv_check2.json()
    inv_updated2 = next(i for i in invoices2 if i["id"] == inv_id)
    assert inv_updated2["status"] == "PAID"
    assert float(inv_updated2["amount_paid"]) == 5000.00
