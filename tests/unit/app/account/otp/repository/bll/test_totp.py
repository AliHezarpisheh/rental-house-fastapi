"""Module defining unit tests for totp business logic layer."""

from unittest import mock

import pytest
from redis.asyncio import Redis

from app.account.otp.helpers.enums import OtpMessages
from app.account.otp.helpers.exceptions import (
    TotpAlreadySetError,
    TotpVerificationAttemptsLimitError,
)
from app.account.otp.repository.bll import TotpBusinessLogicLayer
from config.base import settings


@pytest.fixture
def totp_bll(redis_client: Redis) -> TotpBusinessLogicLayer:
    """Fixture for initializing `TotpBusinessLogicLayer` with Redis client."""
    return TotpBusinessLogicLayer(redis_client=redis_client)


@pytest.fixture
def mock_redis_client() -> mock.AsyncMock:
    """Fixture for mocking an asynchronous `Redis` client."""
    return mock.AsyncMock(spec_set=Redis)


@pytest.mark.asyncio
async def test_set_totp_success(
    totp_bll: TotpBusinessLogicLayer, redis_client: Redis
) -> None:
    """Verify setting totp succeeds and stores correct data with expected TTL."""
    # Arrange
    email = "test@test.com"
    hashed_totp = "hashed_totp"

    # Act
    actual_result = await totp_bll.set_totp(email=email, hashed_totp=hashed_totp)

    # Assert
    expected_result = True
    assert actual_result == expected_result

    key_name = totp_bll.totp_dal._get_totp_key_name(email=email)
    actual_value = await redis_client.hgetall(key_name)
    expected_value = {"hashed_totp": hashed_totp, "attempts": "0"}
    assert actual_value == expected_value

    actual_ttl = await redis_client.ttl(key_name)
    expected_ttl_range = range(settings.otp_ttl - 5, settings.otp_ttl + 1)
    assert actual_ttl in expected_ttl_range


@pytest.mark.asyncio
@pytest.mark.exception
async def test_set_totp_already_set_error_failed(
    totp_bll: TotpBusinessLogicLayer,
) -> None:
    """Verify setting totp raises `TotpAlreadySetError` when totp is already active."""
    # Arrange
    email = "test@test.com"
    hashed_totp = "hashed_totp"
    await totp_bll.set_totp(email=email, hashed_totp=hashed_totp)

    # Act & Assert
    with pytest.raises(TotpAlreadySetError, match=OtpMessages.OTP_ALREADY_ACTIVE.value):
        await totp_bll.set_totp(email=email, hashed_totp=hashed_totp)


@pytest.mark.asyncio
async def test_verify_valid_totp_success(
    totp_bll: TotpBusinessLogicLayer, redis_client: Redis
) -> None:
    """Verify valid totp verification succeeds and removes the stored totp."""
    # Arrange
    totp = "123456"
    hashed_totp = totp_bll.hash_totp(totp=totp)
    email = "test@test.com"
    await totp_bll.set_totp(email=email, hashed_totp=hashed_totp)

    # Act
    actual_result = await totp_bll.verify_totp(email=email, totp=totp)

    # Assert
    expected_result = True
    assert actual_result == expected_result

    # Verify the totp is deleted
    key_name = totp_bll.totp_dal._get_totp_key_name(email=email)
    is_key_exist = await redis_client.exists(key_name)
    assert is_key_exist == 0


@pytest.mark.asyncio
async def test_verify_invalid_totp_success(
    totp_bll: TotpBusinessLogicLayer, redis_client: Redis
) -> None:
    """Verify invalid totp verification fails and increments the attempt counter."""
    # Arrange
    valid_totp = "123456"
    hashed_totp = totp_bll.hash_totp(totp=valid_totp)
    email = "test@test.com"
    await totp_bll.set_totp(email=email, hashed_totp=hashed_totp)

    invalid_totp = "123455"

    # Act
    actual_result = await totp_bll.verify_totp(email=email, totp=invalid_totp)

    # Assert
    expected_result = False
    assert actual_result == expected_result

    # Verify attempt incrimination
    key_name = totp_bll.totp_dal._get_totp_key_name(email=email)
    actual_attempts = await redis_client.hget(key_name, "attempts")
    expected_attempts = 1
    assert int(actual_attempts) == expected_attempts


@pytest.mark.asyncio
@pytest.mark.exception
async def test_verify_otp_attempts_limit_error_failed(
    totp_bll: TotpBusinessLogicLayer,
) -> None:
    """Verify exceeding totp verification attempts raises related error."""
    # Arrange
    totp = "123456"
    hashed_totp = totp_bll.hash_totp(totp=totp)
    email = "test@test.com"
    await totp_bll.set_totp(email=email, hashed_totp=hashed_totp)
    for _ in range(totp_bll.MAX_VERIFY_ATTEMPTS + 1):
        await totp_bll.totp_dal.increment_attempts(email=email)

    # Act & Assert
    with pytest.raises(
        TotpVerificationAttemptsLimitError,
        match=OtpMessages.OTP_TOO_MANY_REQUESTS.value,
    ):
        await totp_bll.verify_totp(email=email, totp=totp)


@pytest.mark.asyncio
async def test_hash_totp_success(totp_bll: TotpBusinessLogicLayer) -> None:
    """Verify hashing totp produces a non-reversible, unique string."""
    # Arrange
    totp = "123456"

    # Act
    hashed_totp = totp_bll.hash_totp(totp=totp)

    # Arrange
    assert isinstance(hashed_totp, str)
    assert totp != hashed_totp


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "totp1, totp2",
    [
        pytest.param("123456", "123455", id="last digit difference"),
        pytest.param("123456", "223456", id="first digit difference"),
        pytest.param("123456", "123356", id="middle digit difference"),
        pytest.param("123456", "214759", id="whole digits difference"),
    ],
)
async def test_hash_totp_different_totp_result_different_hashes_success(
    totp_bll: TotpBusinessLogicLayer, totp1: str, totp2: str
) -> None:
    """Verify different totp values produce different hash results."""
    # Act
    hashed_totp1 = totp_bll.hash_totp(totp=totp1)
    hashed_totp2 = totp_bll.hash_totp(totp=totp2)

    # Assert
    assert hashed_totp1 != hashed_totp2


@pytest.mark.asyncio
async def test_hash_totp_same_totp_result_different_hashes_due_to_salt_success(
    totp_bll: TotpBusinessLogicLayer,
) -> None:
    """Verify the same totp value produces different hashes due to salting."""
    # Arrange
    totp = "123456"

    # Act
    hashed_totp1 = totp_bll.hash_totp(totp=totp)
    hashed_totp2 = totp_bll.hash_totp(totp=totp)

    # Assert
    assert hashed_totp1 != hashed_totp2


@pytest.mark.asyncio
async def test_verify_totp_match_success(totp_bll: TotpBusinessLogicLayer) -> None:
    """Verify correct totp input matches the stored hashed totp."""
    # Arrange
    totp = "123456"
    hashed_totp = totp_bll.hash_totp(totp=totp)

    # Act
    actual_result = totp_bll._verify_totp(totp=totp, hashed_totp=hashed_totp)

    # Assert
    expected_result = True
    assert actual_result == expected_result


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "valid_totp, invalid_totp",
    [
        pytest.param("123456", "123455", id="last digit difference"),
        pytest.param("123456", "223456", id="first digit difference"),
        pytest.param("123456", "123356", id="middle digit difference"),
        pytest.param("123456", "214759", id="whole digits difference"),
    ],
)
async def test_verify_totp_not_match_success(
    totp_bll: TotpBusinessLogicLayer, valid_totp: str, invalid_totp: str
) -> None:
    """Verify incorrect totp inputs do not match the stored hashed totp."""
    # Arrange
    hashed_valid_totp = totp_bll.hash_totp(totp=valid_totp)

    # Act
    actual_result = totp_bll._verify_totp(
        totp=invalid_totp, hashed_totp=hashed_valid_totp
    )

    # Assert
    expected_result = False
    assert actual_result == expected_result


@pytest.mark.asyncio
async def test_verify_totp_empty_input_handled_success(
    totp_bll: TotpBusinessLogicLayer,
) -> None:
    """Verify empty totp input is handled correctly during verification."""
    # Arrange=
    empty_totp = ""
    hashed_totp = totp_bll.hash_totp(totp=empty_totp)

    # Act
    actual_result = totp_bll._verify_totp(totp=empty_totp, hashed_totp=hashed_totp)

    # Assert
    expected_result = True
    assert actual_result == expected_result

    # Arrange
    valid_totp = "123456"
    hashed_valid_totp = totp_bll.hash_totp(totp=valid_totp)

    # Act
    actual_result = totp_bll._verify_totp(
        totp=empty_totp, hashed_totp=hashed_valid_totp
    )

    # Assert
    expected_result = False
    assert actual_result == expected_result
