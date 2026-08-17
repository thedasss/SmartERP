import os
from typing import List, Any, Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User

from app.schemas.documents import DocumentResponse
from app.models.documents import EntityType
from app.services.documents import DocumentService
from app.repositories.documents import DocumentRepository

router = APIRouter()

@router.get("", response_model=List[DocumentResponse])
async def list_documents(
    entity_type: Optional[EntityType] = None,
    entity_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Retrieve documents.
    """
    filters = {"company_id": str(current_user.company_id)}
    if entity_type:
        filters["entity_type"] = entity_type
    if entity_id:
        filters["entity_id"] = entity_id
        
    doc_repo = DocumentRepository(db)
    docs = await doc_repo.get_all(filters=filters, offset=skip, limit=limit)
    return docs[0]

@router.post("/upload", response_model=DocumentResponse, status_code=201)
async def upload_document(
    file: UploadFile = File(...),
    entity_type: EntityType = Form(EntityType.GENERAL),
    entity_id: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Upload a new Document.
    """
    svc = DocumentService(db)
    doc = await svc.upload_file(str(current_user.company_id), file, entity_type, entity_id)
    return doc

@router.get("/{document_id}/download")
async def download_document(
    document_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Download/stream the actual file.
    """
    svc = DocumentService(db)
    doc = await svc.get_document(str(current_user.company_id), document_id)
    
    if not os.path.exists(doc.file_path):
        raise HTTPException(status_code=404, detail="Physical file not found on server")
        
    return FileResponse(
        path=doc.file_path,
        filename=doc.filename,
        media_type=doc.content_type
    )

@router.delete("/{document_id}", status_code=204)
async def delete_document(
    document_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a document and its physical file.
    """
    svc = DocumentService(db)
    await svc.delete_document(str(current_user.company_id), document_id)
