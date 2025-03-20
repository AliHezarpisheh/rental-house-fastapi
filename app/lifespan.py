"""Module for setting lifespan context manager for FastAPI application."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI

from config.base import db, logger, redis_manager


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Set lifespan context manager for FastAPI application."""
    yield
    logger.info("Cleaning up the application...")
    await db.close_engine()
    await redis_manager.disconnect()
