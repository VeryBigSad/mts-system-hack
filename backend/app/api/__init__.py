"""
FastAPI application initialization and configuration.
Sets up CORS middleware and includes API routes.
Provides health check endpoint for monitoring application status.
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.api.routes.health import router as health_router
from app.api.routes.v1 import router as v1_router
from app.core.configs.config import settings
from app.core.db import close_db, init_db
from app.core.logging import setup_logging

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_application: FastAPI) -> AsyncGenerator[None, None]:
    setup_logging(level="DEBUG" if settings.IS_DEBUG else "INFO")
    await init_db()
    logger.info("Application started")

    yield

    await close_db()


if settings.IS_DEBUG:
    kwargs = {"debug": True}
else:
    kwargs = {"debug": False, "docs_url": None, "redoc_url": None, "openapi_url": None}
app = FastAPI(title="MTS System Hackathon backend", lifespan=lifespan, **kwargs)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)
app.include_router(health_router)
app.include_router(v1_router, prefix="/api")
