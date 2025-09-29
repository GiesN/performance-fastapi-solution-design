# -------------------------------------------
# Author: Nils Gies
# -------------------------------------------
"""The main entry point for the API."""

# -------------------------------------------

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse


from app.routers.system import (
    router as system_router,
)


logging.basicConfig(
    format="[%(asctime)s - %(name)s:%(lineno)d - %(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.DEBUG,
)
logger = logging.getLogger(__name__)

app = FastAPI(default_response_class=ORJSONResponse)

cors_origins = [
    "http://localhost",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
logger.info(f"CORS enabled for origins: {cors_origins}")

logger.info("Starting API")
app.include_router(system_router)
