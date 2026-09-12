import re
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.sales import SalesOrder, SOStatus
from app.models.inventory import StockItem
from app.models.finance import Invoice, InvoiceStatus
from app.services.rag import RAGService

try:
    import ollama
except ImportError:
    ollama = None

class AIAssistantService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.rag_service = RAGService(session)

    async def process_query(self, company_id: str, message: str) -> str:
        if ollama is None:
            return "AI features are currently unavailable because the required dependencies (ollama, qdrant-client) are not installed."

        try:
            # 1. Retrieve context from Qdrant
            context_results = await self.rag_service.search_erp_data(message, company_id)
            
            # 2. Format context
            context_text = ""
            if context_results:
                context_texts = [res.get("text", "") for res in context_results]
                context_text = "\n\n".join(context_texts)
            else:
                context_text = "No specific data found in the ERP system."

            # 3. Construct prompt
            system_prompt = f"""You are the SmartERP AI Assistant. You answer questions about the user's business data based ONLY on the provided context below.
If the context does not contain the answer, say "I don't have enough data to answer that."
Be concise and professional. Do not make up information.

CONTEXT:
{context_text}
"""
            # 4. Call Ollama Chat API
            ollama_client = ollama.AsyncClient()
            response = await ollama_client.chat(
                model='llama3',
                messages=[
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user', 'content': message}
                ]
            )
            
            return response.get('message', {}).get('content', 'Sorry, I failed to generate a response.')

        except Exception as e:
            import logging
            import traceback
            logging.error(f"AI Assistant Error: {e}")
            logging.error(traceback.format_exc())
            return f"An error occurred: {str(e)} (Check backend terminal for full traceback)"
