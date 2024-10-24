"""Dependency injection module for redis client dependency."""

from typing import AsyncGenerator

from fastapi import status
from redis.asyncio import Redis, RedisError

from config.base import logger, redis_connection
from toolkit.api.enums import HTTPStatusDoc, Messages, Status
from toolkit.api.exceptions import CustomHTTPException


async def get_redis_client() -> AsyncGenerator[Redis, None]:
    """
    Dependency injection module for Redis client dependency.

    This module provides an asynchronous generator function `get_redis_client` for
    injecting a Redis client instance into FastAPI endpoints. It handles Redis errors
    and unexpected exceptions by logging and raising custom HTTP exceptions.

    Raises
    ------
    CustomHTTPException
        If a Redis error or any other unexpected exception occurs, a custom HTTP
        exception is raised with an appropriate status code and message.

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
Annotated[Redis, Depends(get_redis_client)]):  # noqa: E501
            # Interact with Redis using `redis_client`
            pass
    """
    try:
        redis_client = redis_connection.get_connection()
        yield redis_client
    except CustomHTTPException:
        raise
    except RedisError as err:
        logger.error("Redis error occurred. error: %s", str(err))
        raise CustomHTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            status=Status.ERROR,
            message=Messages.INTERNAL_SERVER_ERROR,
            documentation_link=HTTPStatusDoc.HTTP_STATUS_500,
        )
    except Exception as err:
        logger.critical("Unexpected error occurred. error: %s", str(err))
        raise CustomHTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            status=Status.ERROR,
            message=Messages.INTERNAL_SERVER_ERROR,
            documentation_link=HTTPStatusDoc.HTTP_STATUS_500,
        )
    finally:
        await redis_client.close()
