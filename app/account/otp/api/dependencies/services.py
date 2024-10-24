"""Module containing dependency services for the otp API."""

from typing import Annotated

from fastapi import Depends
from redis.asyncio import Redis

from app.account.otp.repository.services import TotpService
from toolkit.api.redis import get_redis_client


async def get_totp_service(
    redis_client: Annotated[Redis, Depends(get_redis_client)],
) -> TotpService:
    """Get `TotpService` dependency, injecting redis client/connection."""
    return TotpService(redis_client=redis_client)
