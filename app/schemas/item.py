# -------------------------------------------
# Author: Nils Gies
# -------------------------------------------
"""Item schemas for API request/response validation."""

# -------------------------------------------

from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


class ItemBase(BaseModel):
    """Base schema with common item fields."""

    name: str = Field(..., min_length=1, max_length=255, description="Item name")
    description: Optional[str] = Field(None, description="Item description")
    price: Optional[Decimal] = Field(
        None, ge=0, description="Item price (must be non-negative)"
    )
    is_active: bool = Field(True, description="Whether the item is active")


class ItemCreate(ItemBase):
    """Schema for creating a new item."""

    pass


class ItemUpdate(BaseModel):
    """Schema for updating an existing item."""

    name: Optional[str] = Field(
        None, min_length=1, max_length=255, description="Item name"
    )
    description: Optional[str] = Field(None, description="Item description")
    price: Optional[Decimal] = Field(
        None, ge=0, description="Item price (must be non-negative)"
    )
    is_active: Optional[bool] = Field(None, description="Whether the item is active")


class ItemResponse(ItemBase):
    """Schema for item responses."""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="Unique item identifier")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")


class ItemList(BaseModel):
    """Schema for paginated item list responses."""

    items: list[ItemResponse] = Field(..., description="List of items")
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Items per page")
