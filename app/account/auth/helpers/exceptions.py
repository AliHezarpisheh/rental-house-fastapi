"""Module defines exceptions related to auth and users."""

import fastapi

from toolkit.api.enums import HTTPStatusDoc, Status
from toolkit.api.exceptions import (
    DoesNotExistError,
    DuplicateResourceError,
    UnauthorizedError,
)


class TokenError(Exception):
    """Exception raised when a token-related error occur."""

    status_code = fastapi.status.HTTP_401_UNAUTHORIZED
    status = Status.UNAUTHORIZED
    http_status_doc = HTTPStatusDoc.HTTP_STATUS_401


class InternalTokenError(TokenError):
    """Exception raised when a internal token-related error occur."""

    status_code = fastapi.status.HTTP_500_INTERNAL_SERVER_ERROR
    status = Status.ERROR
    http_status_doc = HTTPStatusDoc.HTTP_STATUS_500


class UserDoesNotExistError(DoesNotExistError):
    """Exception raised when a user is not found."""


class DuplicateUserError(DuplicateResourceError):
    """Exception raised when a user already exists."""


class InvalidUserCredentials(UnauthorizedError):
    """Exception raised when the user is not authenticated."""
