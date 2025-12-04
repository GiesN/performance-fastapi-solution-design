# -------------------------------------------
# Author: Nils Gies
# -------------------------------------------
"""Item schemas for API request/response validation (optimized)."""
# -------------------------------------------

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


COMMON_MODEL_CONFIG = ConfigDict(
    validate_assignment=False,  # Disable assignment validation for performance, API schemas are usually immutable after creation and are validated on input and never modified.
    validate_default=False,  # Skip default value validation for performance as defaults are controlled by the codebase.
    str_strip_whitespace=True,  # Strip whitespace from strings
    extra="ignore",  # Ignore extra fields to reduce overhead
)


class ItemBase(BaseModel):
    """Base schema with common item fields (optimized)."""

    model_config = COMMON_MODEL_CONFIG

    name: str = Field(..., min_length=1, max_length=255, description="Item name")
    description: str | None = Field(None, description="Item description")
    price: float | None = Field(
        None, ge=0, description="Item price (must be non-negative)"
    )
    is_active: bool = Field(True, description="Whether the item is active")


class ItemCreate(ItemBase):
    """Schema for creating a new item."""


class ItemUpdate(BaseModel):
    """Schema for updating an existing item (partial)."""

    model_config = COMMON_MODEL_CONFIG

    name: str | None = Field(
        None, min_length=1, max_length=255, description="Item name"
    )
    description: str | None = Field(None, description="Item description")
    price: float | None = Field(
        None, ge=0, description="Item price (must be non-negative)"
    )
    is_active: bool | None = Field(None, description="Whether the item is active")


class ItemResponse(ItemBase):
    """Schema for item responses."""

    model_config = ConfigDict(
        from_attributes=True,
        **COMMON_MODEL_CONFIG,
    )

    id: int = Field(..., description="Unique item identifier")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime | None = Field(None, description="Last update timestamp")


class ItemList(BaseModel):
    """Schema for paginated item list responses."""

    model_config = COMMON_MODEL_CONFIG

    items: list[ItemResponse] = Field(..., description="List of items")
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Items per page")


class ItemQueryParams(BaseModel):
    """Optimized query params model for listing/searching items."""

    model_config = COMMON_MODEL_CONFIG

    page: int = Field(1, ge=1, description="Page number (starts at 1)")
    per_page: int = Field(10, ge=1, le=100, description="Items per page")
    is_active: bool | None = Field(None, description="Filter by active flag")
    q: str | None = Field(
        None,
        min_length=1,
        max_length=255,
        description="Search by name (case-insensitive)",
    )
