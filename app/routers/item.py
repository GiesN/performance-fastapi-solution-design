# -------------------------------------------
# Author: Nils Gies
# -------------------------------------------
"""The items router of the API."""

# -------------------------------------------
from fastapi import APIRouter

router = APIRouter(
    prefix="/items",
    tags=["items"],
)


@router.get("/{item_id}")
async def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}


@router.post("/")
async def create_item(name: str):
    return {"name": name}


@router.put("/{item_id}")
async def update_item(item_id: int, name: str):
    return {"item_id": item_id, "name": name}


@router.patch("/{item_id}")
async def partial_update_item(item_id: int, name: str | None = None):
    return {"item_id": item_id, "name": name}


@router.delete("/{item_id}")
async def delete_item(item_id: int):
    return {"item_id": item_id, "status": "deleted"}
