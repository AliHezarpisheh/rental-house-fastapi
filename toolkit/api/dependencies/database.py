"""Dependency injection module for database session dependencies."""

from typing import AsyncGenerator

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession, async_scoped_session

from config.base import db, logger
from toolkit.api.enums.messages import Messages
from toolkit.api.exceptions import InternalServerError


async def get_async_db_session() -> (
    AsyncGenerator[async_scoped_session[AsyncSession], None]
):
    """
    Dependency injection module for async database session.

    This module provides an asynchronous generator function `get_async_db_session
    for injecting an async scoped database session into FastAPI endpoints. It manages
    database transactions, logging errors, and raising internal errors in case of
    database-related or unexpected issues.

    Raises
    ------
    InternalServerError
        If a SQLAlchemy error or any other unexpected exception occurs, a custom
        internal error is raised.

    Yields
    ------
    AsyncGenerator[async_scoped_session[AsyncSession], None]
        The async scoped session object that can be used for database operations
        within the FastAPI route or service.

    Examples
    --------
    Use this dependency in your FastAPI endpoints to interact with the database:

        @app.get("/some-db-route/")
        async def some_db_route(db_session: \
Annotated[AsyncSession, Depends(get_async_db_session)]):
            # Interact with the database using `db_session`
            pass
    """
    db_session = db.get_session()
    try:
        yield db_session
    except SQLAlchemyError:
        await db_session.rollback()
        logger.error("Unexpected database error", exc_info=True)
        raise InternalServerError(Messages.INTERNAL_SERVER_ERROR.value)
    finally:
        await db_session.close()
