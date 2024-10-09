"""Module for setting lifespan context manager for FastAPI application."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI

from app.account.auth.models import *  # noqa: F403
from config.base import db, logger
from toolkit.database.orm import Base


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Set lifespan context manager for FastAPI application."""
    engine = db.get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables have been created successfully!")
    yield
    logger.info("Disposing database engine...")
    await db.close_engine()
