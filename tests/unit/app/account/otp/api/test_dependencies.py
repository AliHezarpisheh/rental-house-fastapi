"""Module defining unit tests for otp API dependencies."""

from redis.asyncio import Redis

from app.account.otp.api.dependencies import get_totp_service


def test_get_totp_service_success(redis_client: Redis) -> None:
    """Verify the simple functionality of `get_totp_service`."""
    # Act
    actual_totp_service = get_totp_service(redis_client=redis_client)

    # Assert
    assert actual_totp_service.totp_dal.redis_client == redis_client
    assert actual_totp_service.totp_bll.redis_client == redis_client
