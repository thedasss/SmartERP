import os
import uuid
import aiofiles
from fastapi import UploadFile, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.documents import DocumentRepository
from app.models.documents import Document, EntityType

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads")

class DocumentService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.doc_repo = DocumentRepository(session)
        # Ensure upload directory exists
        os.makedirs(UPLOAD_DIR, exist_ok=True)

    async def upload_file(
        self, 
        company_id: str, 
        file: UploadFile, 
        entity_type: EntityType = EntityType.GENERAL, 
        entity_id: str = None
    ) -> Document:
        
        # Generate a unique filename to prevent collisions
        file_ext = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)
        
        # Save file to disk asynchronously
        file_size = 0
        async with aiofiles.open(file_path, 'wb') as out_file:
            while content := await file.read(1024 * 1024):  # read in 1MB chunks
                await out_file.write(content)
                file_size += len(content)
                
        # Create DB record
        doc = await self.doc_repo.create(
            company_id=company_id,
            filename=file.filename,
            file_path=file_path,
            content_type=file.content_type,
            file_size=file_size,
            entity_type=entity_type,
            entity_id=entity_id
        )
        return doc

    async def get_document(self, company_id: str, doc_id: str) -> Document:
        doc = await self.doc_repo.get_by_id(doc_id)
        if not doc or str(doc.company_id) != company_id:
            raise HTTPException(status_code=404, detail="Document not found")
        return doc

    async def delete_document(self, company_id: str, doc_id: str):
        doc = await self.get_document(company_id, doc_id)
        
        # Delete from DB
        await self.doc_repo.delete(doc)
        
        # Delete physical file
        if os.path.exists(doc.file_path):
            try:
                os.remove(doc.file_path)
            except OSError as e:
                print(f"Warning: Failed to delete physical file {doc.file_path}: {e}")
