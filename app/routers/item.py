# -------------------------------------------
# Author: Nils Gies
# -------------------------------------------
"""The items router of the API (async)."""
# -------------------------------------------
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.utils.database import get_db
from app.schemas.item import (
    ItemCreate,
    ItemUpdate,
    ItemResponse,
    ItemList,
    ItemQueryParams,
)
from app.dataclasses.item import ItemData, ItemUpdateData
from app.crud.item import item_crud

router = APIRouter(prefix="/items", tags=["items"])


# Note:
# Incoming Request: POST /items
#          ↓
# FastAPI detects Depends(get_db)
#          ↓
# Calls get_db() function
#          ↓
# Enters async context manager (opens session)
#          ↓
# Yields session to route handler
#          ↓
# Route handler executes: create_item(item_in, db=session)
#          ↓
# Route handler returns response
#          ↓
# FastAPI resumes get_db() after yield
#          ↓
# Session cleanup (closes connection, returns to pool)
#          ↓
# Response sent to client
@router.post("/", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
async def create_item(item_in: ItemCreate, db: AsyncSession = Depends(get_db)):
    """Create a new item."""
    internal = ItemData(**item_in.model_dump())
    item = await item_crud.create(db, internal.to_dict())
    return item


@router.get("/{item_id}", response_model=ItemResponse, summary="Get an item by ID")
async def read_item(item_id: int, db: AsyncSession = Depends(get_db)):
    """Retrieve a single item by ID."""
    item = await item_crud.get(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.get("/", response_model=ItemList, summary="List items (paginated)")
async def list_items(
    params: ItemQueryParams = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """List items with pagination, optional active filter and search."""
    skip = (params.page - 1) * params.per_page

    if params.q:
        results = await item_crud.search_by_name(db, params.q)
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

    items = await item_crud.get_multi(
        db, skip=skip, limit=params.per_page, is_active=params.is_active
    )
    total = await item_crud.count(db, is_active=params.is_active)
    return ItemList(
        items=items,
        total=total,
        page=params.page,
        per_page=params.per_page,
    )


@router.put("/{item_id}", response_model=ItemResponse)
async def update_item(
    item_id: int,
    item_in: ItemUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update (replace) an item."""
    update_dc = ItemUpdateData(**item_in.model_dump(exclude_unset=True))
    updated = await item_crud.update(db, item_id, update_dc.to_patch_dict())
    if not updated:
        raise HTTPException(status_code=404, detail="Item not found")
    return updated


@router.patch("/{item_id}", response_model=ItemResponse)
async def partial_update_item(
    item_id: int,
    item_in: ItemUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Partial update an item."""
    update_dc = ItemUpdateData(**item_in.model_dump(exclude_unset=True))
    updated = await item_crud.update(db, item_id, update_dc.to_patch_dict())
    if not updated:
        raise HTTPException(status_code=404, detail="Item not found")
    return updated


@router.delete("/{item_id}", response_model=ItemResponse)
async def delete_item(
    item_id: int,
    permanent: bool = Query(False, description="Permanently delete if true"),
    db: AsyncSession = Depends(get_db),
):
    """Soft delete (deactivate) or permanently delete an item."""
    if permanent:
        success = await item_crud.hard_delete(db, item_id)
        if not success:
            raise HTTPException(status_code=404, detail="Item not found")
        raise HTTPException(status_code=410, detail="Item permanently deleted")

    deleted = await item_crud.delete(db, item_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Item not found")
    return deleted
