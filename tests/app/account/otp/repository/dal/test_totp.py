"""Module defining unit tests for totp data access layer."""

from unittest import mock

import pytest
import redis
from redis.asyncio import Redis

from app.account.otp.helpers.exceptions import (
    TotpAttemptsIncriminationError,
    TotpCreationFailedError,
    TotpRemovalFailedError,
    TotpVerificationFailedError,
)
from app.account.otp.repository.dal import TotpDataAccessLayer
from tests.conftest import settings


@pytest.fixture
def totp_dal(redis_client: Redis) -> TotpDataAccessLayer:
    """Fixture for initializing `TotpDataAccessLayer` with Redis client."""
    return TotpDataAccessLayer(redis_client=redis_client)


@pytest.fixture
def mock_redis_client() -> mock.AsyncMock:
    """Fixture for mocking an asynchronous `Redis` client."""
    return mock.AsyncMock(spec_set=Redis)


@pytest.mark.asyncio
async def test_set_totp_success(
    totp_dal: TotpDataAccessLayer, redis_client: Redis
) -> None:
    """Verify setting totp succeeds and data is correctly stored."""
    # Arrange
    email = "test@test.com"
    hashed_totp = "test_hashed_totp"

    # Act
    actual_result = await totp_dal.set_totp(email=email, hashed_totp=hashed_totp)

    # Assert
    expected_result = True
    assert actual_result == expected_result

    key_name = totp_dal._get_totp_key_name(email=email)

    actual_mapping = await redis_client.hgetall(key_name)
    expected_mapping = totp_dal._get_totp_mapping(hashed_totp=hashed_totp)
    assert actual_mapping.get("hashed_totp") == expected_mapping.get("hashed_totp")
    assert int(actual_mapping.get("attempts")) == int(expected_mapping.get("attempts"))

    actual_ttl = await redis_client.ttl(key_name)
    expected_ttl_range = range(settings.otp_ttl - 5, settings.otp_ttl + 1)
    assert actual_ttl in expected_ttl_range


@pytest.mark.asyncio
@pytest.mark.exception
async def test_set_totp_creation_failed(mock_redis_client: Redis) -> None:
    """Verify totp creation failure raises `TotpCreationFailedError`."""
    # Arrange
    mock_pipeline = mock.AsyncMock()
    mock_pipeline.execute.return_value = [0, "doesn't matter"]
    mock_redis_client.pipeline.return_value = mock_pipeline
    totp_dal = TotpDataAccessLayer(redis_client=mock_redis_client)

    email = "test@test.com"
    hashed_totp = "test_hashed_totp"

    # Act & Assert
    with pytest.raises(
        TotpCreationFailedError, match="Totp creation failed. Check the logs!"
    ):
        await totp_dal.set_totp(email=email, hashed_totp=hashed_totp)


@pytest.mark.asyncio
async def test_get_totp_success(totp_dal: TotpDataAccessLayer) -> None:
    """Verify retrieving a stored totp succeeds."""
    # Arrange
    email = "test@test.com"
    hashed_totp = "hashed_totp"

    await totp_dal.set_totp(email=email, hashed_totp=hashed_totp)

    # Act
    actual_result = await totp_dal.get_totp(email=email)

    # Assert
    expected_result = hashed_totp
    assert actual_result == expected_result


@pytest.mark.asyncio
@pytest.mark.exception
async def test_get_unset_totp_failed(totp_dal: TotpDataAccessLayer) -> None:
    """Verify retrieving an unset totp raises `TotpVerificationFailedError`."""
    # Arrange
    email = "test@test.com"

    # Act & Assert
    with pytest.raises(
        TotpVerificationFailedError,
        match=(
            "Totp verification failed. Totp expiration reached or no totp was created."
        ),
    ):
        await totp_dal.get_totp(email=email)


@pytest.mark.asyncio
async def test_delete_totp_success(totp_dal: TotpDataAccessLayer) -> None:
    """Verify deleting a stored totp succeeds."""
    # Arrange
    email = "test@test.com"
    hashed_totp = "hashed_totp"

    await totp_dal.set_totp(email=email, hashed_totp=hashed_totp)

    # Act
    actual_result = await totp_dal.delete_totp(email=email)

    # Assert
    expected_result = True
    assert actual_result == expected_result

    with pytest.raises(
        TotpVerificationFailedError,
        match=(
            "Totp verification failed. Totp expiration reached or no totp was created."
        ),
    ):
        await totp_dal.get_totp(email=email)


@pytest.mark.asyncio
@pytest.mark.exception
async def test_delete_unset_totp_failed(totp_dal: TotpDataAccessLayer) -> None:
    """Verify deleting an unset totp raises `TotpRemovalFailedError`."""
    # Arrange
    email = "test@test.com"

    # Act
    with pytest.raises(
        TotpRemovalFailedError, match="Totp removal failed. Check the logs!"
    ):
        await totp_dal.delete_totp(email=email)


@pytest.mark.asyncio
async def test_check_totp_success(
    totp_dal: TotpDataAccessLayer, redis_client: Redis
) -> None:
    """Verify checking totp existence returns correct boolean values."""
    # Arrange
    existing_email = "test@test.com"
    existing_key = totp_dal._get_totp_key_name(email=existing_email)
    await redis_client.set(existing_key, 1)

    not_existing_email = ":("

    # Act
    actual_result_existing_key = await totp_dal.check_totp(email=existing_email)
    actual_result_not_existing_key = await totp_dal.check_totp(email=not_existing_email)

    # Assert
    expected_result_existing_key = True
    assert actual_result_existing_key == expected_result_existing_key

    expected_result_not_existing_key = False
    assert actual_result_not_existing_key == expected_result_not_existing_key


@pytest.mark.asyncio
async def test_increment_attempts_success(
    totp_dal: TotpDataAccessLayer, redis_client: Redis
) -> None:
    """Verify incrementing totp attempts updates the stored value correctly."""
    # Arrange
    email = "test@test.com"
    hashed_totp = "hashed_totp"

    await totp_dal.set_totp(email=email, hashed_totp=hashed_totp)

    # Act
    await totp_dal.increment_attempts(email=email)

    # Assert
    key_name = totp_dal._get_totp_key_name(email=email)

    actual_attempts = await redis_client.hget(key_name, "attempts")
    expected_attempts = 1
    assert int(actual_attempts) == expected_attempts

    # Act
    await totp_dal.increment_attempts(email=email)

    # Assert
    actual_attempts = await redis_client.hget(key_name, "attempts")
    expected_attempts = 2
    assert int(actual_attempts) == expected_attempts


@pytest.mark.asyncio
@pytest.mark.exception
async def test_increment_attempts_response_error_failed(
    mock_redis_client: mock.AsyncMock,
) -> None:
    """Verify incrementing totp attempts raises related error due to `Redis` error."""
    # Arrange
    email = "test@test.com"

    mock_redis_client.hincrby.side_effect = redis.exceptions.ResponseError
    totp_dal = TotpDataAccessLayer(redis_client=mock_redis_client)

    # Act & Assert
    with pytest.raises(
        TotpAttemptsIncriminationError,
        match="Error while working with totp data. Check the logs!",
    ):
        await totp_dal.increment_attempts(email=email)


@pytest.mark.asyncio
async def test_get_attempts_success(totp_dal: TotpDataAccessLayer) -> None:
    """Verify retrieving totp attempts returns the correct count."""
    # Arrange
    email = "test@test.com"
    hashed_totp = "hashed_totp"

    await totp_dal.set_totp(email=email, hashed_totp=hashed_totp)

    # Act
    actual_result = await totp_dal.get_attempts(email=email)

    # Assert
    expected_result = 0
    assert actual_result == expected_result

    # Arrange
    await totp_dal.increment_attempts(email=email)
    await totp_dal.increment_attempts(email=email)

    # Act
    actual_result = await totp_dal.get_attempts(email=email)

    # Assert
    expected_result = 2
    assert actual_result == expected_result


@pytest.mark.asyncio
async def test_get_invalid_attempts_success(totp_dal: TotpDataAccessLayer) -> None:
    """Verify retrieving attempts for an unset totp returns -1."""
    # Arrange
    email = "test@test.com"

    # Act
    actual_result = await totp_dal.get_attempts(email=email)

    # Assert
    expected_result = -1
    assert actual_result == expected_result


@pytest.mark.asyncio
async def test_set_expiration_redis_client_success(
    totp_dal: TotpDataAccessLayer, redis_client: Redis
) -> None:
    """Verify setting expiration for a key using Redis client succeeds."""
    # Arrange
    key_name = "test"
    key_value = "test"
    ttl = 10

    await redis_client.set(key_name, key_value)

    # Act
    await totp_dal.set_expiration(key_name=key_name, ttl=ttl)

    # Assert
    actual_ttl = await redis_client.ttl(key_name)
    expected_ttl_range = range(ttl - 5, ttl + 1)
    assert actual_ttl in expected_ttl_range


@pytest.mark.asyncio
async def test_set_expiration_redis_pipeline_success(
    totp_dal: TotpDataAccessLayer, redis_client: Redis
) -> None:
    """Verify setting expiration for a key using Redis pipeline succeeds."""
    # Arrange
    key_name = "test"
    key_value = "test"
    ttl = 10

    redis_pipeline = redis_client.pipeline()

    await redis_pipeline.set(key_name, key_value)

    # Act
    await totp_dal.set_expiration(key_name=key_name, ttl=ttl, pipeline=redis_pipeline)

    # Assert
    assert len(redis_pipeline) == 2

    # Act
    await redis_pipeline.execute()

    # Assert
    actual_ttl = await redis_client.ttl(key_name)
    expected_ttl_range = range(ttl - 5, ttl + 1)
    assert actual_ttl in expected_ttl_range

    assert len(redis_pipeline) == 0


@pytest.mark.asyncio
@pytest.mark.exception
async def test_set_expiration_redis_failed(totp_dal: TotpDataAccessLayer) -> None:
    """Verify setting expiration raises `TotpCreationFailedError` on Redis failure."""
    # Arrange
    key_name = "test"
    ttl = 10

    redis_pipeline = mock.AsyncMock()
    redis_pipeline.expire.return_value = 0

    # Act & Assert
    with pytest.raises(
        TotpCreationFailedError, match="Totp creation failed. Check the logs!"
    ):
        await totp_dal.set_expiration(
            key_name=key_name, ttl=ttl, pipeline=redis_pipeline
        )


def test_get_totp_key_name(totp_dal: TotpDataAccessLayer) -> None:
    """Verify generating totp key name follows the correct format."""
    # Arrange
    email = "test@test.com"

    # Act & Assert
    actual_totp_key_name = totp_dal._get_totp_key_name(email=email)
    expected_totp_key_name = f"totp:users:{email}"
    assert actual_totp_key_name == expected_totp_key_name


def test_get_totp_mapping(totp_dal: TotpDataAccessLayer) -> None:
    """Verify generating totp mapping returns expected dictionary structure."""
    # Arrange
    hashed_totp = "test_hashed_totp"

    # Act & Assert
    actual_totp_mapping = totp_dal._get_totp_mapping(hashed_totp=hashed_totp)
    expected_totp_mapping = {"hashed_totp": hashed_totp, "attempts": 0}
    assert actual_totp_mapping == expected_totp_mapping
