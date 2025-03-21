"""Module defining unit tests for the database dependencies."""

from unittest import mock

import pytest
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from config.database import AsyncDatabaseConnection
from toolkit.api.dependencies.database import get_async_db_session
from toolkit.api.enums import Messages
from toolkit.api.exceptions import InternalServerError


@pytest.fixture
def mock_db_session() -> mock.AsyncMock:
    """Fixture providing a mocked async database session."""
    return mock.AsyncMock(spec_set=AsyncSession)


@pytest.fixture
def mock_db(mock_db_session: mock.AsyncMock) -> mock.AsyncMock:
    """Fixture providing a mocked database connection."""
    db = mock.AsyncMock(spec_set=AsyncDatabaseConnection)
    db.get_session.return_value = mock_db_session
    return db


@pytest.mark.asyncio
async def test_get_async_db_session_success(
    mock_db_session: mock.AsyncMock, mock_db: mock.AsyncMock
) -> None:
    """Verify successful retrieval of an async database session."""
    # Arrange
    with mock.patch("toolkit.api.dependencies.database.db", new=mock_db):
        get_async_db_session_generator = get_async_db_session()

        # Act
        db_session = await anext(get_async_db_session_generator)

        # Assert
        mock_db.get_session.assert_called_once_with()
        assert db_session == mock_db_session

        with pytest.raises(StopAsyncIteration):
            await anext(get_async_db_session_generator)
        mock_db_session.close.assert_awaited_once_with()


@pytest.mark.asyncio
async def test_get_async_db_session_sqlalchemy_error(
    mock_db_session: mock.AsyncMock, mock_db: mock.AsyncMock
) -> None:
    """Verify handling of `SQLAlchemyError` during session retrieval."""
    # Arrange
    with mock.patch("toolkit.api.dependencies.database.db", new=mock_db):
        get_async_db_session_generator = get_async_db_session()
        await anext(get_async_db_session_generator)

        # Act & Assert
        with pytest.raises(
            InternalServerError, match=Messages.INTERNAL_SERVER_ERROR.value
        ):
            await get_async_db_session_generator.athrow(SQLAlchemyError("Test error"))

        # Verify rollback was called
        mock_db_session.rollback.assert_awaited_once()
        mock_db_session.close.assert_awaited_once()
