"""Module containing dependency functions for the totp API."""

from typing import Annotated

from fastapi import Depends
from redis.asyncio import Redis

from app.account.otp.repository.services import TotpService
from toolkit.api.dependencies import get_async_redis_client


def get_totp_service(
    redis_client: Annotated[Redis, Depends(get_async_redis_client)],
) -> TotpService:
    """Get `TotpService` dependency, injecting redis client/connection."""
    return TotpService(redis_client=redis_client)
