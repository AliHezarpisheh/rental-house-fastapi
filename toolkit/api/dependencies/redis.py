"""Dependency injection module for redis client dependency."""

from typing import AsyncGenerator

from redis.asyncio import Redis, RedisError

from config.base import logger, redis_manager
from toolkit.api.enums import Messages
from toolkit.api.exceptions import InternalServerError


async def get_async_redis_client() -> AsyncGenerator[Redis, None]:
    """
    Dependency injection module for Redis client dependency.

    This module provides an asynchronous generator function `get_async_redis_client` for
    injecting a Redis client instance into FastAPI endpoints. It handles Redis errors
    and unexpected exceptions by logging and raising internal server errors.

    Raises
    ------
    InternalServerError
        If a Redis error or any other unexpected exception occurs, an internal server
        error is raised.

    Yields
    ------
    AsyncGenerator[Redis, None]
        The Redis client instance that can be used for Redis operations within the
        FastAPI route or service.

    Examples
    --------
    Use this dependency in your FastAPI endpoints to interact with Redis:

        @app.get("/some-redis-route/")
        async def some_redis_route(redis_client: \
Annotated[Redis, Depends(get_async_redis_client)]):  # noqa: E501
            # Interact with Redis using `redis_client`
            pass
    """
    try:
        redis_client = redis_manager.get_connection()
        yield redis_client
    except RedisError:
        logger.error("Unexpected redis error", exc_info=True)
        raise InternalServerError(Messages.INTERNAL_SERVER_ERROR.value)
    finally:
        await redis_client.close()
