"""Module defining unit tests for the redis dependencies."""

from unittest import mock

import pytest
from redis.asyncio import Redis
from redis.exceptions import RedisError

from config.redis import AsyncRedisConnection
from toolkit.api.dependencies.redis import get_async_redis_client
from toolkit.api.enums.messages import Messages
from toolkit.api.exceptions import InternalServerError


@pytest.fixture
def mock_redis() -> mock.AsyncMock:
    """Fixture providing a mocked async redis client/connection."""
    redis = mock.AsyncMock(spec_set=Redis)
    redis.close = mock.AsyncMock()
    return redis


@pytest.fixture
def mock_redis_manager(mock_redis: mock.AsyncMock) -> mock.AsyncMock:
    """Fixture providing a mocked redis manager."""
    redis_manager = mock.AsyncMock(spec_set=AsyncRedisConnection)
    redis_manager.get_connection.return_value = mock_redis
    return redis_manager


@pytest.mark.asyncio
async def test_get_async_redis_client_success(
    mock_redis: mock.AsyncMock, mock_redis_manager: mock.AsyncMock
) -> None:
    """Verify successful retrieval of an async redis client."""
    # Arrange
    with mock.patch(
        "toolkit.api.dependencies.redis.redis_manager", new=mock_redis_manager
    ):
        get_async_redis_client_generator = get_async_redis_client()

        # Act
        redis_client = await anext(get_async_redis_client_generator)

        # Assert
        assert redis_client == mock_redis
        mock_redis_manager.get_connection.assert_called_once_with()


@pytest.mark.asyncio
async def test_get_async_redis_client_redis_error(
    mock_redis: mock.AsyncMock, mock_redis_manager: mock.AsyncMock
) -> None:
    """Verify handling of `RedisError` during client retrieval."""
    # Arrange
    with mock.patch(
        "toolkit.api.dependencies.redis.redis_manager", new=mock_redis_manager
    ):
        get_async_redis_client_generator = get_async_redis_client()
        await anext(get_async_redis_client_generator)

        # Act & Assert
        with pytest.raises(
            InternalServerError, match=Messages.INTERNAL_SERVER_ERROR.value
        ):
            await get_async_redis_client_generator.athrow(RedisError("Test error"))

        mock_redis.close.assert_awaited_once_with()
