# -------------------------------------------
# Author: Nils Gies
# -------------------------------------------
"""CRUD operations for Item model (async)."""
# -------------------------------------------

from typing import Optional, List, Mapping, Any
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.item import Item


class ItemCRUD:
    """Async CRUD operations for Item model."""

    async def create(self, db: AsyncSession, data: Mapping[str, Any]) -> Item:
        """Create a new item."""
        db_item = Item(**data)
        db.add(db_item)
        await db.commit()
        await db.refresh(db_item)
        return db_item

    async def get(self, db: AsyncSession, item_id: int) -> Optional[Item]:
        """Get an item by ID."""
        result = await db.execute(select(Item).where(Item.id == item_id))
        return result.scalar_one_or_none()

    async def get_multi(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = None,
    ) -> List[Item]:
        """Get multiple items with optional filtering."""
        stmt = select(Item)

        if is_active is not None:
            stmt = stmt.where(Item.is_active == is_active)

        stmt = stmt.offset(skip).limit(limit)
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def update(
        self, db: AsyncSession, item_id: int, changes: Mapping[str, Any]
    ) -> Optional[Item]:
        """Update an existing item."""
        db_item = await self.get(db, item_id)
        if not db_item:
            return None

        for field, value in changes.items():
            setattr(db_item, field, value)

        await db.commit()
        await db.refresh(db_item)
        return db_item

    async def delete(self, db: AsyncSession, item_id: int) -> Optional[Item]:
        """Soft delete an item (set is_active to False)."""
        db_item = await self.get(db, item_id)
        if not db_item:
            return None

        db_item.is_active = False
        await db.commit()
        await db.refresh(db_item)
        return db_item

    async def hard_delete(self, db: AsyncSession, item_id: int) -> bool:
        """Permanently delete an item."""
        db_item = await self.get(db, item_id)
        if not db_item:
            return False

        await db.delete(db_item)
        await db.commit()
        return True

    async def count(self, db: AsyncSession, is_active: Optional[bool] = None) -> int:
        """Count items with optional filtering."""
        stmt = select(func.count()).select_from(Item)

        if is_active is not None:
            stmt = stmt.where(Item.is_active == is_active)

        result = await db.execute(stmt)
        return result.scalar_one()

    async def search_by_name(self, db: AsyncSession, name: str) -> List[Item]:
        """Search items by name (case-insensitive partial match)."""
        stmt = select(Item).where(Item.name.ilike(f"%{name}%"))
        result = await db.execute(stmt)
        return list(result.scalars().all())


# Create instance
item_crud = ItemCRUD()
