import pytest
import os
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_documents_flow(client: AsyncClient, token_headers: dict):
    # 1. Create a dummy file for testing
    file_content = b"Hello, this is a test document."
    test_filename = "test_doc.txt"
    with open(test_filename, "wb") as f:
        f.write(file_content)

    try:
        # 2. Upload Document
        with open(test_filename, "rb") as f:
            files = {"file": (test_filename, f, "text/plain")}
            data = {"entity_type": "GENERAL"}
            
            upload_resp = await client.post(
                "/api/v1/documents/upload",
                headers=token_headers,
                data=data,
                files=files
            )
            
        assert upload_resp.status_code == 201
        doc_data = upload_resp.json()
        doc_id = doc_data["id"]
        assert doc_data["filename"] == test_filename
        assert doc_data["content_type"] == "text/plain"

        # 3. List Documents
        list_resp = await client.get("/api/v1/documents", headers=token_headers)
        assert list_resp.status_code == 200
        docs = list_resp.json()
        assert any(d["id"] == doc_id for d in docs)
        
        # 4. Download Document
        dl_resp = await client.get(f"/api/v1/documents/{doc_id}/download", headers=token_headers)
        assert dl_resp.status_code == 200
        assert dl_resp.content == file_content
        
        # 5. Delete Document
        del_resp = await client.delete(f"/api/v1/documents/{doc_id}", headers=token_headers)
        assert del_resp.status_code == 204
        
        # 6. Verify Deletion
        list_resp2 = await client.get("/api/v1/documents", headers=token_headers)
        docs2 = list_resp2.json()
        assert not any(d["id"] == doc_id for d in docs2)

    finally:
        # Cleanup dummy file
        if os.path.exists(test_filename):
            os.remove(test_filename)
