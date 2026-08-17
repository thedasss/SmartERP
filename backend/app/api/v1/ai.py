import asyncio
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User

from app.schemas.ai import AIChatRequest, AIChatResponse
from app.services.ai import AIAssistantService
from app.services.rag import RAGService

router = APIRouter()

@router.post("/chat", response_model=AIChatResponse)
async def chat_with_ai(
    data: AIChatRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Send a message to the AI assistant.
    """
    # Simulate a slight delay to feel like an AI is "thinking"
    await asyncio.sleep(1)
    
    svc = AIAssistantService(db)
    reply = await svc.process_query(str(current_user.company_id), data.message)
    
    return {"reply": reply}

@router.post("/index")
async def index_data(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Index all ERP data into Qdrant for RAG.
    """
    svc = RAGService(db)
    result = await svc.index_erp_data(str(current_user.company_id))
    return {"message": result}
