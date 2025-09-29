# -------------------------------------------
# Author: Nils Gies
# -------------------------------------------
"""CRUD operations for Item model."""

# -------------------------------------------

from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.item import Item
from app.schemas.item import ItemCreate, ItemUpdate


class ItemCRUD:
    """CRUD operations for Item model."""

    def create(self, db: Session, item_in: ItemCreate) -> Item:
        """Create a new item."""
        db_item = Item(**item_in.model_dump())
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        return db_item

    def get(self, db: Session, item_id: int) -> Optional[Item]:
        """Get an item by ID."""
        return db.query(Item).filter(Item.id == item_id).first()

    def get_multi(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = None,
    ) -> List[Item]:
        """Get multiple items with optional filtering."""
        query = db.query(Item)

        if is_active is not None:
            query = query.filter(Item.is_active == is_active)

        return query.offset(skip).limit(limit).all()

    def update(self, db: Session, item_id: int, item_in: ItemUpdate) -> Optional[Item]:
        """Update an existing item."""
        db_item = self.get(db, item_id)
        if not db_item:
            return None

        update_data = item_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_item, field, value)

        db.commit()
        db.refresh(db_item)
        return db_item

    def delete(self, db: Session, item_id: int) -> Optional[Item]:
        """Soft delete an item (set is_active to False)."""
        db_item = self.get(db, item_id)
        if not db_item:
            return None

        db_item.is_active = False
        db.commit()
        db.refresh(db_item)
        return db_item

    def hard_delete(self, db: Session, item_id: int) -> bool:
        """Permanently delete an item."""
        db_item = self.get(db, item_id)
        if not db_item:
            return False

        db.delete(db_item)
        db.commit()
        return True

    def count(self, db: Session, is_active: Optional[bool] = None) -> int:
        """Count items with optional filtering."""
        query = db.query(Item)

        if is_active is not None:
            query = query.filter(Item.is_active == is_active)

        return query.count()

    def search_by_name(self, db: Session, name: str) -> List[Item]:
        """Search items by name (case-insensitive partial match)."""
        return db.query(Item).filter(Item.name.ilike(f"%{name}%")).all()


# Create instance
item_crud = ItemCRUD()
