"""
Module defining integration tests for totp API.

While most business logic is covered by integration tests, the `otp` module is primarily
used through `TotpService`, which has comprehensive test coverage. As a result, the
totp API tests remain simple and minimal.
"""

from collections.abc import Generator
from unittest import mock

import pytest
from fastapi import status
from httpx import AsyncClient

from app.account.otp.helpers.enums import OtpMessages
from app.account.otp.repository.services.totp import TotpService
from toolkit.api.enums import HTTPStatusDoc, Status


@pytest.fixture(scope="module", autouse=True)
def mock_send_otp_email() -> Generator[None, None, None]:
    """Mock celery task, preventing actual task generation."""
    with mock.patch(
        "app.account.otp.repository.services.totp.send_otp_email", autospec=True
    ):
        yield


@pytest.mark.asyncio
async def test_send_totp_success(async_api_client: AsyncClient) -> None:
    """Verify that sending a totp succeeds with valid input."""
    # Arrange
    endpoint = "/users/totp/send"
    payload = {"email": "test@test.com"}

    # Act
    response = await async_api_client.post(endpoint, json=payload)

    # Assert
    actual_status_code = response.status_code
    expected_status_code = status.HTTP_201_CREATED
    assert actual_status_code == expected_status_code

    actual_json = response.json()
    expected_json = {
        "status": Status.CREATED.value,
        "message": OtpMessages.OTP_SEND_SUCCESS.value,
        "documentationLink": HTTPStatusDoc.HTTP_STATUS_201.value,
    }
    assert actual_json == expected_json


@pytest.mark.asyncio
async def test_verify_totp_success(async_api_client: AsyncClient) -> None:
    """Verify that totp verification succeeds with a correct code."""
    # Arrange
    email = "test@test.com"
    totp = "123456"
    endpoint = "/users/totp/verify"
    payload = {"email": email, "totp": totp}

    with mock.patch.object(TotpService, "_generate_totp", return_value=totp):
        await async_api_client.post("/users/totp/send", json={"email": email})

    # Act
    response = await async_api_client.post(endpoint, json=payload)

    # Assert
    actual_status_code = response.status_code
    expected_status_code = status.HTTP_200_OK
    assert actual_status_code == expected_status_code

    actual_json = response.json()
    expected_json = {
        "status": Status.SUCCESS.value,
        "message": OtpMessages.OTP_VERIFICATION_SUCCESS.value,
        "documentationLink": HTTPStatusDoc.HTTP_STATUS_200.value,
    }
    assert actual_json == expected_json


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "totp, invalid_totp",
    [
        pytest.param("123456", "123455", id="last_digit_difference"),
        pytest.param("123456", "223456", id="first_digit_difference"),
        pytest.param("123456", "123356", id="middle_digit_difference"),
        pytest.param("123456", "214759", id="whole_digits_difference"),
    ],
)
async def test_verify_invalid_totp(
    async_api_client: AsyncClient, totp: str, invalid_totp: str
) -> None:
    """Verify that totp verification fails with various incorrect codes."""
    # Arrange
    email = "test@test.com"
    endpoint = "/users/totp/verify"
    payload = {"email": email, "totp": invalid_totp}

    with mock.patch.object(TotpService, "_generate_totp", return_value=totp):
        await async_api_client.post("/users/totp/send", json={"email": email})

    # Act
    response = await async_api_client.post(endpoint, json=payload)

    # Assert
    actual_status_code = response.status_code
    expected_status_code = status.HTTP_403_FORBIDDEN
    assert actual_status_code == expected_status_code

    actual_json = response.json()
    expected_json = {
        "status": Status.FORBIDDEN.value,
        "message": OtpMessages.OTP_VERIFICATION_FAILED.value,
        "documentationLink": HTTPStatusDoc.HTTP_STATUS_403.value,
    }
    assert actual_json == expected_json
