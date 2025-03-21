"""Module defining unit tests for application lifespan contextmanager."""

from unittest import mock

from fastapi.testclient import TestClient

from app.main import app
from config.database import AsyncDatabaseConnection
from config.redis import AsyncRedisConnection


def test_lifespan() -> None:
    """Verify that database and Redis connections close properly during app shutdown."""
    # Arrange
    mock_db = mock.AsyncMock(spec_set=AsyncDatabaseConnection)
    mock_redis_manager = mock.AsyncMock(spec_set=AsyncRedisConnection)

    with mock.patch("app.lifespan.db", mock_db), mock.patch(
        "app.lifespan.redis_manager", mock_redis_manager
    ):
        # Act
        with TestClient(app=app):
            pass

        # Assert
        mock_db.close_engine.assert_awaited_once_with()
        mock_redis_manager.disconnect.assert_awaited_once_with()
