from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from app.models.documents import EntityType

class DocumentResponse(BaseModel):
    id: str
    filename: str
    content_type: str
    file_size: int
    entity_type: EntityType
    entity_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
