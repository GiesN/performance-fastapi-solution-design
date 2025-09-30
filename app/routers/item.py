# -------------------------------------------
# Author: Nils Gies
# -------------------------------------------
"""The items router of the API."""
# -------------------------------------------
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.utils.database import get_db
from app.schemas.item import (
    ItemCreate,
    ItemUpdate,
    ItemResponse,
    ItemList,
    ItemQueryParams,
)
from app.crud.item import item_crud
from app.dataclasses.item import ItemData, ItemUpdateData

router = APIRouter(prefix="/items", tags=["items"])


@router.post("/", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
def create_item(item_in: ItemCreate, db: Session = Depends(get_db)):
    internal = ItemData(**item_in.model_dump())
    item = item_crud.create(db, internal.to_dict())
    return item


@router.get("/{item_id}", response_model=ItemResponse, summary="Get an item by ID")
def read_item(item_id: int, db: Session = Depends(get_db)):
    item = item_crud.get(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.get("/", response_model=ItemList, summary="List items (paginated)")
def list_items(params: ItemQueryParams = Depends(), db: Session = Depends(get_db)):
    skip = (params.page - 1) * params.per_page
    if params.q:
        results = item_crud.search_by_name(db, params.q)
        if params.is_active is not None:
            results = [r for r in results if r.is_active == params.is_active]
        total = len(results)
        page_items = results[skip : skip + params.per_page]
        return ItemList(
            items=page_items,
            total=total,
            page=params.page,
            per_page=params.per_page,
        )
    items = item_crud.get_multi(
        db, skip=skip, limit=params.per_page, is_active=params.is_active
    )
    total = item_crud.count(db, is_active=params.is_active)
    return ItemList(
        items=items,
        total=total,
        page=params.page,
        per_page=params.per_page,
    )


@router.put("/{item_id}", response_model=ItemResponse)
def update_item(item_id: int, item_in: ItemUpdate, db: Session = Depends(get_db)):
    update_dc = ItemUpdateData(**item_in.model_dump(exclude_unset=True))
    updated = item_crud.update(db, item_id, update_dc.to_patch_dict())
    if not updated:
        raise HTTPException(status_code=404, detail="Item not found")
    return updated


@router.patch("/{item_id}", response_model=ItemResponse)
def partial_update_item(
    item_id: int, item_in: ItemUpdate, db: Session = Depends(get_db)
):
    update_dc = ItemUpdateData(**item_in.model_dump(exclude_unset=True))
    updated = item_crud.update(db, item_id, update_dc.to_patch_dict())
    if not updated:
        raise HTTPException(status_code=404, detail="Item not found")
    return updated


@router.delete(
    "/{item_id}",
    response_model=ItemResponse,
    summary="Soft delete an item",
)
def delete_item(
    item_id: int,
    permanent: bool = Query(False, description="Permanently delete if true"),
    db: Session = Depends(get_db),
):
    if permanent:
        ok = item_crud.hard_delete(db, item_id)
        if not ok:
            raise HTTPException(status_code=404, detail="Item not found")
        raise HTTPException(status_code=410, detail="Item permanently deleted")
    deleted = item_crud.delete(db, item_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Item not found")
    return deleted
