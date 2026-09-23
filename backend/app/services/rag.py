import uuid
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.product import Product
from app.models.sales import SalesOrder
from app.models.procurement import PurchaseOrder
from app.models.finance import Invoice

try:
    import ollama
    from qdrant_client import AsyncQdrantClient
    from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
except ImportError:
    ollama = None
    AsyncQdrantClient = None

# Global clients to prevent file lock issues with Qdrant local mode
_qdrant_client = None
_ollama_client = None

if AsyncQdrantClient is not None:
    _qdrant_client = AsyncQdrantClient(path="qdrant_data")
    _ollama_client = ollama.AsyncClient()

class RAGService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.collection_name = "smarterp_docs"
        self.embed_model = "nomic-embed-text"
        self.qdrant = _qdrant_client
        self.ollama_client = _ollama_client

    async def init_collection(self):
        """Ensure the collection exists in Qdrant."""
        if not self.qdrant: return
        
        collections = await self.qdrant.get_collections()
        exists = any(c.name == self.collection_name for c in collections.collections)
        if not exists:
            await self.qdrant.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=768, distance=Distance.COSINE),
            )

    async def get_embedding(self, text: str) -> List[float]:
        """Generate embedding using local Ollama model."""
        if not self.ollama_client: return []
        
        response = await self.ollama_client.embeddings(
            model=self.embed_model,
            prompt=text
        )
        return response.get('embedding', [])

    async def index_erp_data(self, company_id: str):
        """Extract data from DB, chunk it, embed it, and store in Qdrant."""
        if not self.qdrant: return "Dependencies not installed"
        
        await self.init_collection()
        points = []

        # 1. Index Products
        products = (await self.session.execute(select(Product).where(Product.company_id == company_id))).scalars().all()
        for p in products:
            text = f"Product: {p.name}\nSKU: {p.sku}\nCategory: {p.category}\nPrice: ${p.price}\nCost: ${p.cost}\nDescription: {p.description}"
            embedding = await self.get_embedding(text)
            if embedding:
                points.append(
                    PointStruct(
                        id=str(uuid.uuid4()),
                        vector=embedding,
                        payload={"company_id": str(company_id), "type": "product", "text": text, "source_id": str(p.id)}
                    )
                )

        # 2. Index Sales Orders
        # Due to complexity, we'll index high-level order stats
        sales_orders = (await self.session.execute(select(SalesOrder).where(SalesOrder.company_id == company_id))).unique().scalars().all()
        for so in sales_orders:
            text = f"Sales Order: {so.so_number}\nStatus: {so.status}\nTotal Amount: ${so.total_amount}\nCreated At: {so.created_at}"
            embedding = await self.get_embedding(text)
            if embedding:
                points.append(
                    PointStruct(
                        id=str(uuid.uuid4()),
                        vector=embedding,
                        payload={"company_id": str(company_id), "type": "sales_order", "text": text, "source_id": str(so.id)}
                    )
                )

        # 3. Index Invoices
        invoices = (await self.session.execute(select(Invoice).where(Invoice.company_id == company_id))).unique().scalars().all()
        for inv in invoices:
            text = f"Invoice: {inv.invoice_number}\nStatus: {inv.status}\nTotal Amount: ${inv.total_amount}\nAmount Paid: ${inv.amount_paid}\nDue Date: {inv.due_date}"
            embedding = await self.get_embedding(text)
            if embedding:
                points.append(
                    PointStruct(
                        id=str(uuid.uuid4()),
                        vector=embedding,
                        payload={"company_id": str(company_id), "type": "invoice", "text": text, "source_id": str(inv.id)}
                    )
                )

        # Upsert all points
        if points:
            # Upsert in batches of 100
            batch_size = 100
            for i in range(0, len(points), batch_size):
                batch = points[i:i + batch_size]
                await self.qdrant.upsert(
                    collection_name=self.collection_name,
                    points=batch
                )

        return f"Successfully indexed {len(points)} documents."

    async def search_erp_data(self, query: str, company_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search Qdrant for context related to the query."""
        if not self.qdrant: return []
        
        query_vector = await self.get_embedding(query)
        if not query_vector: return []

        search_result = await self.qdrant.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            query_filter=Filter(
                must=[
                    FieldCondition(
                        key="company_id",
                        match=MatchValue(value=str(company_id)),
                    )
                ]
            ),
            limit=limit,
        )

        results = []
        for hit in search_result.points:
            results.append(hit.payload)
        return results
