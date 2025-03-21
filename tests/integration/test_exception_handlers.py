"""Module defining integration tests for the exception handlers."""

from unittest import mock

import pytest
from fastapi import status
from httpx import AsyncClient

from config.database import AsyncDatabaseConnection
from toolkit.api.enums import HTTPStatusDoc, Status


@pytest.mark.asyncio
async def test_request_validation_exception_handler(
    async_api_client: AsyncClient,
) -> None:
    """Verify that the request validation exception handler functions correctly."""
    # Arrange
    endpoint = "/users/totp/send"
    invalid_payload = {
        "not-email": "I am using totp api to validate the exception handler"
    }

    # Act
    response = await async_api_client.post(endpoint, json=invalid_payload)

    # Assert
    actual_status_code = response.status_code
    expected_status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    assert actual_status_code == expected_status_code

    actual_json = {
        "status": Status.VALIDATION_ERROR.value,
        "message": "Field required",
        "details": {"field": "email", "reason": "missing"},
        "documentationLink": HTTPStatusDoc.HTTP_STATUS_422.value,
    }
    expected_json = response.json()
    assert actual_json == expected_json


@pytest.mark.asyncio
async def test_internal_exception_handler(async_api_client: AsyncClient) -> None:
    """Verify that the internal exception handler properly handles unexpected errors."""
    # Arrange
    # Setting a sid_effect on the methods called in health-check endpoint to check the
    # internal exception handler.
    endpoint = "/health-check"
    mock_db = mock.AsyncMock(spec_set=AsyncDatabaseConnection)
    mock_db.test_connection.side_effect = Exception("test exceptions")
    with mock.patch("app.healthcheck.db", mock_db):
        # Act & Assert
        with pytest.raises(Exception, match="test exception"):
            await async_api_client.get(endpoint)
