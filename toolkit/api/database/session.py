"""Dependency injection module for database session dependency, mainly the session."""

from typing import AsyncGenerator

from fastapi import status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession, async_scoped_session

from config.base import db, logger
from toolkit.api.enums import HTTPStatusDoc, Messages, Status
from toolkit.api.exceptions import CustomHTTPException


async def get_async_db_session() -> (
    AsyncGenerator[async_scoped_session[AsyncSession], None]
):
    """
    Get an async scoped database session.

    Yields
    ------
    sqlalchemy.ext.async_scoped_session[AsyncSession]
        An async scoped session object.
    """
    db_session = db.get_session()
    try:
        yield db_session
    except CustomHTTPException:
        raise
    except SQLAlchemyError:
        await db_session.rollback()
        logger.error("Database error occurred", exc_info=True)
        raise CustomHTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            status=Status.ERROR,
            message=Messages.INTERNAL_SERVER_ERROR,
            documentation_link=HTTPStatusDoc.STATUS_500,
        )
    except Exception:
        await db_session.rollback()
        logger.critical("Unexpected error occurred.", exc_info=True)
        raise
    finally:
        await db_session.close()
