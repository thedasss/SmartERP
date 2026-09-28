import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_ai_chat_flow(client: AsyncClient, token_headers: dict):
    # 1. Test Sales Intent
    resp1 = await client.post(
        "/api/v1/ai/chat",
        headers=token_headers,
        json={"message": "What are my total sales?"}
    )
    assert resp1.status_code == 200
    assert "sales revenue" in resp1.json()["reply"].lower()

    # 2. Test Inventory Intent
    resp2 = await client.post(
        "/api/v1/ai/chat",
        headers=token_headers,
        json={"message": "Show me my inventory"}
    )
    assert resp2.status_code == 200
    assert "in stock" in resp2.json()["reply"].lower()
    
    # 3. Test Fallback
    resp3 = await client.post(
        "/api/v1/ai/chat",
        headers=token_headers,
        json={"message": "What is the meaning of life?"}
    )
    assert resp3.status_code == 200
    assert "not sure how to answer" in resp3.json()["reply"].lower()
