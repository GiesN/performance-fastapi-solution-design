# -------------------------------------------
# Author: Nils Gies
# -------------------------------------------
"""CRUD operations for Item model (decoupled from Pydantic)."""
# -------------------------------------------

from typing import Optional, List, Mapping, Any
from sqlalchemy.orm import Session

from app.models.item import Item


class ItemCRUD:
    def create(self, db: Session, data: Mapping[str, Any]) -> Item:
        db_item = Item(**data)
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        return db_item

    def get(self, db: Session, item_id: int) -> Optional[Item]:
        return db.query(Item).filter(Item.id == item_id).first()

    def get_multi(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = None,
    ) -> List[Item]:
        query = db.query(Item)
        if is_active is not None:
            query = query.filter(Item.is_active == is_active)
        return query.offset(skip).limit(limit).all()

    def update(
        self, db: Session, item_id: int, changes: Mapping[str, Any]
    ) -> Optional[Item]:
        db_item = self.get(db, item_id)
        if not db_item:
            return None
        for field, value in changes.items():
            setattr(db_item, field, value)
        db.commit()
        db.refresh(db_item)
        return db_item

    def delete(self, db: Session, item_id: int) -> Optional[Item]:
        db_item = self.get(db, item_id)
        if not db_item:
            return None
        db_item.is_active = False
        db.commit()
        db.refresh(db_item)
        return db_item

    def hard_delete(self, db: Session, item_id: int) -> bool:
        db_item = self.get(db, item_id)
        if not db_item:
            return False
        db.delete(db_item)
        db.commit()
        return True

    def count(self, db: Session, is_active: Optional[bool] = None) -> int:
        query = db.query(Item)
        if is_active is not None:
            query = query.filter(Item.is_active == is_active)
        return query.count()

    def search_by_name(self, db: Session, name: str):
        return db.query(Item).filter(Item.name.ilike(f"%{name}%")).all()


item_crud = ItemCRUD()
