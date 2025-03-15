"""Custom fixtures, hooks, and configurations for pytest tests."""

from collections.abc import AsyncGenerator

import pytest
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient
from redis.asyncio import Redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_scoped_session

from app.main import app
from config.database import AsyncDatabaseConnection
from config.redis import AsyncRedisConnection
from config.settings.base import Settings
from toolkit.api.dependencies import get_async_db_session, get_async_redis_client
from toolkit.database.orm import Base

settings = Settings()  # Use this instead of config.base.settings object in testing


# Database-related hooks


@pytest.fixture(scope="session")
def db() -> AsyncDatabaseConnection:
    """Async database connection objects for testing."""
    return AsyncDatabaseConnection(database_url=settings.database_url)


@pytest.fixture
async def db_engine(db: AsyncDatabaseConnection) -> AsyncGenerator[None, None]:
    """
    Fixture providing a SQLAlchemy async engine instance connected to the database.

    The main purpose of the fixture is creating and dropping tables, at start and end
    of the test session. Also, it close the engine after the test session.

    Parameters
    ----------
    db : AsyncDatabaseConnection
        The object for managing database objects.

    Yields
    ------
    Generator[Engine, None, None]
        A generator yielding the SQLAlchemy engine instance.
    """
    engine = db.get_engine()

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await db.close_engine()


@pytest.fixture
async def db_session(
    db: AsyncDatabaseConnection, db_engine: AsyncEngine
) -> AsyncGenerator[async_scoped_session[AsyncSession], None]:
    """
    Fixture providing an async scoped SQLAlchemy session.

    Parameters
    ----------
    db : AsyncDatabaseConnection
        The object for managing database objects.

    Returns
    -------
    async_scoped_session[AsyncSession]
        An async scoped SQLAlchemy session.
    """
    session = db.get_session()
    yield session
    await session.rollback()

    # Truncate all tables after each test function.
    for table in reversed(Base.metadata.sorted_tables):
        stmt = text(f"TRUNCATE {table.name} CASCADE;")
        await session.execute(stmt)
        await session.commit()

    await session.close()


@pytest.fixture(autouse=True)
def override_get_async_db_session(
    db_session: async_scoped_session[AsyncSession], db_engine: AsyncEngine
) -> None:
    """
    Override the `get_async_db_session` dependency to use the provided database session.

    Parameters
    ----------
    db_session : async_scoped_session[AsyncSession]
        The test database session to be used instead of the default session.
    """

    async def _get_async_test_db_session() -> (
        AsyncGenerator[async_scoped_session[AsyncSession], None]
    ):
        """
        Get a test database session.

        Yields
        ------
        Session
            A test database session.
        """
        yield db_session

    app.dependency_overrides[get_async_db_session] = _get_async_test_db_session


# Redis-related hooks


@pytest.fixture(scope="session")
def redis_manager() -> AsyncRedisConnection:
    """
    Fixture providing an asynchronous Redis connection manager.

    This fixture initializes a Redis connection with the specified configuration
    settings for use in tests.

    Returns
    -------
    AsyncRedisConnection
        The Redis connection manager instance.
    """
    return AsyncRedisConnection(
        host=settings.redis_host,
        port=settings.redis_port,
        db=settings.redis_db,
        password=settings.redis_password,
        max_connection=settings.redis_pool_max_connection,
    )


@pytest.fixture
async def redis_client(
    redis_manager: AsyncRedisConnection,
) -> AsyncGenerator[Redis, None]:
    """
    Fixture providing an asynchronous Redis client.

    This fixture yields a Redis connection instance for test use and ensures
    that all keys are removed after the test completes to maintain a clean
    testing environment.

    Parameters
    ----------
    redis_manager : AsyncRedisConnection
        The Redis connection manager providing the connection instance.

    Yields
    ------
    Redis
        A Redis client instance for interacting with the database.
    """
    connection = redis_manager.get_connection()
    yield connection
    all_keys = await connection.keys()
    for key in all_keys:
        await connection.unlink(key)
    await connection.aclose()


@pytest.fixture(autouse=True)
def override_get_async_redis_client(redis_client: Redis) -> None:
    """
    Override the `get_async_redis_client` dependency to use the provided redis client.

    Parameters
    ----------
    redis_client : Redis
        The test client to be used instead of the default client.
    """

    async def _get_async_test_redis_client() -> AsyncGenerator[Redis, None]:
        """
        Get a test redis client.

        Yields
        ------
        Redis
            A test redis client.
        """
        yield redis_client

    app.dependency_overrides[get_async_redis_client] = _get_async_test_redis_client


# API-related hooks


@pytest.fixture(scope="session")
def sync_api_client() -> TestClient:
    """Fixture to create a synchronous FastAPI test client."""
    return TestClient(app=app)


@pytest.fixture
async def async_api_client() -> AsyncGenerator[AsyncClient, None]:
    """Fixture to create an asynchronous FastAPI test client."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client
