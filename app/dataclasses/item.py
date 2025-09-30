# -------------------------------------------
# Author: Nils Gies
# -------------------------------------------
"""Lightweight internal item dataclasses (no Pydantic overhead)."""
# -------------------------------------------
from dataclasses import dataclass, asdict, fields
from typing import Optional


@dataclass(slots=True)
class ItemData:
    name: str
    description: Optional[str]
    price: Optional[float]
    is_active: bool = True

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(slots=True)
class ItemUpdateData:
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    is_active: Optional[bool] = None

    def to_patch_dict(self) -> dict:
        return {
            f.name: getattr(self, f.name)
            for f in fields(self)
            if getattr(self, f.name) is not None
        }
