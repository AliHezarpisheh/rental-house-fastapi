"""Module defines exceptions related to auth and users."""

import fastapi

from toolkit.api.enums import HTTPStatusDoc, Status
from toolkit.api.exceptions import APIException, DoesNotExistError, DuplicateError


class UserDoesNotExistError(DoesNotExistError):
    """Exception raised when a user is not found."""


class UserDuplicateError(DuplicateError):
    """Exception raised when a user already exists."""


class UserInvalidCredentials(APIException):
    """Exception raised when the user is not authenticated."""

    status_code = fastapi.status.HTTP_401_UNAUTHORIZED
    status = Status.FORBIDDEN
    documentation_link = HTTPStatusDoc.HTTP_STATUS_401


class UserAlreadyRegisteredError(APIException):
    """Exception raised when a registered user wants to register again."""

    status_code = fastapi.status.HTTP_409_CONFLICT
    status = Status.CONFLICT
    documentation_link = HTTPStatusDoc.HTTP_STATUS_409


class UserAlreadyVerified(APIException):
    """Exception raised when a verified user wants to verified again."""

    status_code = fastapi.status.HTTP_409_CONFLICT
    status = Status.CONFLICT
    documentation_link = HTTPStatusDoc.HTTP_STATUS_409


class TokenError(Exception):
    """Exception raised when a token-related error occur."""

    status_code = fastapi.status.HTTP_401_UNAUTHORIZED
    status = Status.UNAUTHORIZED
    documentation_link = HTTPStatusDoc.HTTP_STATUS_401


class InternalTokenError(TokenError):
    """Exception raised when a internal token-related error occur."""

    status_code = fastapi.status.HTTP_500_INTERNAL_SERVER_ERROR
    status = Status.ERROR
    documentation_link = HTTPStatusDoc.HTTP_STATUS_500
