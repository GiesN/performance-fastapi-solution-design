# -------------------------------------------
# Author: Nils Gies
# -------------------------------------------
"""The systems router endpoints."""

# -------------------------------------------
import datetime

from fastapi import APIRouter, HTTPException
from starlette import status

router = APIRouter()


@router.get("/health", status_code=status.HTTP_200_OK)
async def check_health():
    """Standard health checker"""
    try:
        response = {
            "timestamp": datetime.datetime.now().isoformat(),
            "message": "api reporting for duty!",
        }
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {e!s}",
        ) from e
