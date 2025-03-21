"""Module provides a health check endpoint for the FastAPI application."""

from typing import Any

from fastapi import APIRouter, status
from pydantic import BaseModel

from config.base import db, redis_manager
from toolkit.api.exceptions import ServiceUnavailableError

router = APIRouter(prefix="/health-check", tags=["Health Check"])


class HealthCheckResponse(BaseModel):
    """
    Model for health check response.

    Attributes
    ----------
    database : bool
        Indicates if the database is available.
    redis : bool
        Indicates if the redis is available.
    message : str
        Message indicating the health status.
    """

    database: bool
    redis: bool
    message: str


@router.get(
    "",
    response_model=HealthCheckResponse,
    status_code=status.HTTP_200_OK,
    description="Perform a health check on the service.",
)
async def check_health() -> Any:
    """
    Perform a health check to ensure all the necessary connections are available.

    Returns
    -------
    Any
        JSON response indicating the health status of the database and redis.

    Raises
    ------
    ServiceUnavailableError
        If the database connection or redis are not available, raises a 503 HTTP error.
    """
    is_db_available = await db.test_connection()
    if not is_db_available:
        raise ServiceUnavailableError(message="Database not available")
    is_redis_available = await redis_manager.test_connection()
    if not is_redis_available:
        raise ServiceUnavailableError(message="Redis not available")
    return {
        "database": is_db_available,
        "redis": is_redis_available,
        "message": "Everything is Fine!",
    }
