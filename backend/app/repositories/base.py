"""
Generic async base repository providing common CRUD operations.
All entity-specific repositories should extend this.
"""
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import Base

ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository(Generic[ModelT]):
    def __init__(self, model: Type[ModelT], session: AsyncSession):
        self.model = model
        self.session = session

    async def get_by_id(self, entity_id: str) -> Optional[ModelT]:
        result = await self.session.execute(
            select(self.model).where(self.model.id == entity_id)
        )
        return result.unique().scalar_one_or_none()

    async def get_all(
        self,
        filters: Optional[Dict[str, Any]] = None,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[List[ModelT], int]:
        """Return (items, total_count) for the given filters."""
        query = select(self.model)
        if filters:
            for key, val in filters.items():
                if val is not None and hasattr(self.model, key):
                    query = query.where(getattr(self.model, key) == val)

        # Soft-delete filter
        if hasattr(self.model, "is_deleted"):
            query = query.where(self.model.is_deleted.is_(False))

        count_query = select(func.count()).select_from(query.subquery())
        total = (await self.session.execute(count_query)).scalar_one()

        result = await self.session.execute(query.offset(offset).limit(limit))
        items = list(result.unique().scalars().all())
        return items, total

    async def create(self, **kwargs) -> ModelT:
        instance = self.model(**kwargs)
        self.session.add(instance)
        await self.session.flush()  # Get PK without committing
        await self.session.refresh(instance)
        return instance

    async def update(self, instance: ModelT, **kwargs) -> ModelT:
        for key, value in kwargs.items():
            if value is not None and hasattr(instance, key):
                setattr(instance, key, value)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def delete(self, instance: ModelT) -> None:
        await self.session.delete(instance)
        await self.session.flush()

    async def soft_delete(self, instance: ModelT) -> ModelT:
        """Mark as deleted without physically removing the row."""
        from datetime import datetime, timezone
        instance.is_deleted = True
        instance.deleted_at = datetime.now(timezone.utc)
        await self.session.flush()
        return instance
