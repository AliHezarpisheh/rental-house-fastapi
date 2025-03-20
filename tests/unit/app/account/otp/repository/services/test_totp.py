"""Module defines unit tests for the `TotpService`."""

from unittest import mock

import pytest
from redis.asyncio import Redis

from app.account.otp.helpers.exceptions import (
    TotpCreationFailedError,
    TotpVerificationAttemptsLimitError,
    TotpVerificationFailedError,
)
from app.account.otp.repository.bll.totp import TotpBusinessLogicLayer
from app.account.otp.repository.dal.totp import TotpDataAccessLayer
from app.account.otp.repository.services import TotpService
from tests.conftest import settings
from toolkit.api.enums import HTTPStatusDoc, Status
from toolkit.api.exceptions.custom_exceptions import ValidationError


@pytest.fixture
def totp_service(redis_client: Redis) -> TotpService:
    """Fixture provide a `TotpService` instance with `Redis` dependencies."""
    totp_dal = TotpDataAccessLayer(redis_client=redis_client)
    totp_bll = TotpBusinessLogicLayer(redis_client=redis_client)
    return TotpService(totp_dal=totp_dal, totp_bll=totp_bll)


@pytest.mark.asyncio
async def test_set_totp_success(totp_service: TotpService, redis_client: Redis) -> None:
    """Verify totp is set successfully and stored correctly in Redis."""
    # Arrange
    email = "test@test.com"
    totp = "123456"
    hashed_totp = totp_service.totp_bll.hash_totp(totp=totp)
    with mock.patch(
        "app.account.otp.repository.services.totp.send_otp_email", autospec=True
    ) as mock_send_otp_email, mock.patch.object(
        TotpService, "_generate_totp", return_value=totp
    ):
        # Act
        actual_result = await totp_service.set_totp(email=email)

        # Assert
        expected_result = {
            "status": Status.CREATED,
            "message": "Otp sent successfully.",
            "documentation_link": HTTPStatusDoc.HTTP_STATUS_201,
        }
        assert actual_result == expected_result

        # Verify the totp is actually set in the database with correct values
        key_name = totp_service.totp_dal._get_totp_key_name(email=email)
        totp_redis_value = await redis_client.hgetall(key_name)
        assert totp_redis_value["hashed_totp"] != totp
        # Due to different salts, every hash should be different, even for the same totp
        assert totp_redis_value["hashed_totp"] != hashed_totp
        assert totp_redis_value["attempts"] == "0"

        # Verify the totp is actually set in the database with correct ttl
        actual_ttl = await redis_client.ttl(key_name)
        expected_ttl_range = range(settings.otp_ttl - 5, settings.otp_ttl + 1)
        assert actual_ttl in expected_ttl_range

        mock_send_otp_email.delay.assert_called_once_with(to_email=email, otp=totp)


@pytest.mark.asyncio
@pytest.mark.exception
@pytest.mark.parametrize(
    "email",
    [
        pytest.param("plainaddress", id="missing_at_and_domain"),
        pytest.param("@missingusername.com", id="missing_username"),
        pytest.param("username@", id="missing_domain"),
        pytest.param("username@.com", id="invalid_domain"),
        pytest.param("username@com", id="missing_tld"),
        pytest.param("username@domain..com", id="double_dot_in_domain"),
        pytest.param("user name@domain.com", id="space_in_email"),
        pytest.param("user@domain@another.com", id="multiple_at_symbols"),
        pytest.param("user@domain.c", id="invalid_tld"),
    ],
)
async def test_set_totp_failed_due_to_invalid_email_format(
    email: str, totp_service: TotpService
) -> None:
    """Verify totp creation fails for invalid email formats."""
    # Arrange
    totp = "123456"
    with mock.patch(
        "app.account.otp.repository.services.totp.send_otp_email", autospec=True
    ), mock.patch.object(TotpService, "_generate_totp", return_value=totp):
        # Act
        with pytest.raises(ValidationError, match="Invalid email format"):
            await totp_service.set_totp(email=email)


@pytest.mark.asyncio
@pytest.mark.exception
async def test_set_totp_failed_due_to_unknown_issue(redis_client: Redis) -> None:
    """Verify totp creation fails when an unknown issue occurs."""
    # Arrange
    totp_dal = TotpDataAccessLayer(redis_client=redis_client)
    mock_bll = mock.AsyncMock(spec_set=TotpBusinessLogicLayer)
    mock_bll.set_totp.return_value = False
    totp_service = TotpService(totp_dal=totp_dal, totp_bll=mock_bll)

    email = "test@test.com"
    totp = "123456"
    with mock.patch(
        "app.account.otp.repository.services.totp.send_otp_email", autospec=True
    ), mock.patch.object(TotpService, "_generate_totp", return_value=totp):
        # Act
        with pytest.raises(
            TotpCreationFailedError, match="Failed to set otp. Contact support."
        ):
            await totp_service.set_totp(email=email)


@pytest.mark.asyncio
async def test_verify_totp_success(
    totp_service: TotpService, redis_client: Redis
) -> None:
    """Verify totp is successfully validated and removed from `Redis`."""
    # Arrange
    email = "test@test.com"
    totp = "123456"
    with mock.patch(
        "app.account.otp.repository.services.totp.send_otp_email", autospec=True
    ), mock.patch.object(TotpService, "_generate_totp", return_value=totp):
        await totp_service.set_totp(email=email)

        # Act
        actual_result = await totp_service.verify_totp(email=email, totp=totp)

        # Assert
        expected_result = {
            "status": Status.SUCCESS,
            "message": "Otp verified successfully.",
            "documentation_link": HTTPStatusDoc.HTTP_STATUS_200,
        }
        assert actual_result == expected_result

        # Verify that the key is removed from the database
        key_name = totp_service.totp_dal._get_totp_key_name(email=email)
        is_key_exists = await redis_client.exists(key_name)
        assert is_key_exists == 0


@pytest.mark.asyncio
@pytest.mark.exception
@pytest.mark.parametrize(
    "totp, invalid_totp",
    [
        pytest.param("123456", "123455", id="last_digit_difference"),
        pytest.param("123456", "223456", id="first_digit_difference"),
        pytest.param("123456", "123356", id="middle_digit_difference"),
        pytest.param("123456", "214759", id="whole_digits_difference"),
    ],
)
async def test_verify_totp_failed_due_to_unknown_issue(
    totp: str, invalid_totp: str, totp_service: TotpService
) -> None:
    """Verify totp validation fails for incorrect totp values."""
    # Arrange
    email = "test@test.com"
    with mock.patch(
        "app.account.otp.repository.services.totp.send_otp_email", autospec=True
    ), mock.patch.object(TotpService, "_generate_totp", return_value=totp):
        await totp_service.set_totp(email=email)

        # Act & Assert
        with pytest.raises(TotpVerificationFailedError, match="Incorrect otp."):
            await totp_service.verify_totp(email=email, totp=invalid_totp)


@pytest.mark.asyncio
@pytest.mark.exception
@pytest.mark.parametrize(
    "invalid_email",
    [
        pytest.param("plainaddress", id="missing_at_and_domain"),
        pytest.param("@missingusername.com", id="missing_username"),
        pytest.param("username@", id="missing_domain"),
        pytest.param("username@.com", id="invalid_domain"),
        pytest.param("username@com", id="missing_tld"),
        pytest.param("username@domain..com", id="double_dot_in_domain"),
        pytest.param("user name@domain.com", id="space_in_email"),
        pytest.param("user@domain@another.com", id="multiple_at_symbols"),
        pytest.param("user@domain.c", id="invalid_tld"),
    ],
)
async def test_verify_totp_failed_due_to_invalid_email_format(
    invalid_email: str, totp_service: TotpService
) -> None:
    """Verify totp validation fails for invalid email formats."""
    # Arrange
    email = "test@test.com"
    totp = "123456"
    with mock.patch(
        "app.account.otp.repository.services.totp.send_otp_email", autospec=True
    ), mock.patch.object(TotpService, "_generate_totp", return_value=totp):
        await totp_service.set_totp(email=email)

        # Act & Assert
        with pytest.raises(ValidationError, match="Invalid email format"):
            await totp_service.verify_totp(email=invalid_email, totp=totp)


@pytest.mark.asyncio
@pytest.mark.exception
@pytest.mark.parametrize(
    "invalid_totp",
    [
        None,
        pytest.param(123456, id="integer"),
        pytest.param(12345.6, id="float"),
    ],
)
async def test_verify_totp_failed_due_to_invalid_totp_type(
    invalid_totp: str, totp_service: TotpService
) -> None:
    """Verify totp validation fails for non-string OTP values."""
    # Arrange
    email = "test@test.com"
    totp = "123456"
    with mock.patch(
        "app.account.otp.repository.services.totp.send_otp_email", autospec=True
    ), mock.patch.object(TotpService, "_generate_totp", return_value=totp):
        await totp_service.set_totp(email=email)

        # Act & Assert
        with pytest.raises(AssertionError, match="totp should be instance of `str`"):
            await totp_service.verify_totp(email=email, totp=invalid_totp)


@pytest.mark.asyncio
@pytest.mark.exception
@pytest.mark.parametrize(
    "invalid_totp",
    [
        "no_digit_at_all",
        "some12digits56",
        pytest.param("", id="empty_string"),
        pytest.param("21346m", id="mostly_digits"),
    ],
)
async def test_verify_totp_failed_due_to_invalid_totp_not_digits(
    invalid_totp: str, totp_service: TotpService
) -> None:
    """Verify totp validation fails when otp contains non-digit characters."""
    # Arrange
    email = "test@test.com"
    totp = "123456"
    with mock.patch(
        "app.account.otp.repository.services.totp.send_otp_email", autospec=True
    ), mock.patch.object(TotpService, "_generate_totp", return_value=totp):
        await totp_service.set_totp(email=email)

        # Act & Assert
        with pytest.raises(ValidationError, match="Totp should be just digits"):
            await totp_service.verify_totp(email=email, totp=invalid_totp)


@pytest.mark.asyncio
@pytest.mark.exception
@pytest.mark.parametrize(
    "invalid_totp",
    [
        pytest.param("1" * (settings.otp_digits - 1), id="too_short"),
        pytest.param("1" * (settings.otp_digits + 1), id="too_long"),
    ],
)
async def test_verify_totp_failed_due_to_invalid_totp_length(
    invalid_totp: str, totp_service: TotpService
) -> None:
    """Verify totp validation fails for incorrect OTP length."""
    # Arrange
    email = "test@test.com"
    totp = "123456"
    with mock.patch(
        "app.account.otp.repository.services.totp.send_otp_email", autospec=True
    ), mock.patch.object(TotpService, "_generate_totp", return_value=totp):
        await totp_service.set_totp(email=email)

        # Act & Assert
        with pytest.raises(
            ValidationError, match=f"Totp should be {settings.otp_digits} digits"
        ):
            await totp_service.verify_totp(email=email, totp=invalid_totp)


@pytest.mark.asyncio
@pytest.mark.exception
async def test_verify_totp_rate_limit(totp_service: TotpService) -> None:
    """Verify totp verification fails after exceeding max retry attempts."""
    # Arrange
    email = "test@test.com"
    totp = "123456"
    with mock.patch(
        "app.account.otp.repository.services.totp.send_otp_email", autospec=True
    ), mock.patch.object(TotpService, "_generate_totp", return_value=totp):
        await totp_service.set_totp(email=email)

        for _ in range(totp_service.totp_bll.MAX_VERIFY_ATTEMPTS):
            try:
                await totp_service.verify_totp(email=email, totp="123455")
            except TotpVerificationFailedError:
                pass

        # Act & Assert
        with pytest.raises(
            TotpVerificationAttemptsLimitError,
            match="Too much requests for verifying totp.",
        ):
            await totp_service.verify_totp(email=email, totp=totp)


@pytest.mark.asyncio
async def test_verify_expired_totp(
    totp_service: TotpService, redis_client: Redis
) -> None:
    """Verify totp validation fails for expired or missing otp."""
    # Arrange
    email = "test@test.com"
    totp = "123456"
    with mock.patch(
        "app.account.otp.repository.services.totp.send_otp_email", autospec=True
    ), mock.patch.object(TotpService, "_generate_totp", return_value=totp):
        await totp_service.set_totp(email=email)

        # Simulate ttl expiration
        key_name = totp_service.totp_dal._get_totp_key_name(email=email)
        await redis_client.unlink(key_name)

        # Act & Assert
        with pytest.raises(
            TotpVerificationFailedError,
            match=(
                "Totp verification failed. Totp expiration reached or no totp was "
                "created."
            ),
        ):
            await totp_service.verify_totp(email=email, totp=totp)


def test_generate_totp_success(totp_service: TotpService) -> None:
    """Verify totp generation produces a valid numeric otp of correct length."""
    # Act
    for _ in range(10):
        totp = totp_service._generate_totp()

        # Assert
        assert isinstance(totp, str)
        assert len(totp) == settings.otp_digits
        assert totp.isdigit()
