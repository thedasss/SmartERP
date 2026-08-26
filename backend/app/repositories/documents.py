from sqlalchemy.ext.asyncio import AsyncSession
from app.models.documents import Document
from app.repositories.base import BaseRepository

class DocumentRepository(BaseRepository[Document]):
    def __init__(self, session: AsyncSession):
        super().__init__(Document, session)
