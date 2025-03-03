"""Module defines exceptions related to OTPs."""

import fastapi

from toolkit.api.enums import HTTPStatusDoc, Status
from toolkit.api.exceptions import APIException


class TotpVerificationFailedError(APIException):
    """Exception raised when TOTP verification fails."""

    status_code = fastapi.status.HTTP_403_FORBIDDEN
    status = Status.FORBIDDEN
    documentation_link = HTTPStatusDoc.HTTP_STATUS_403


class TotpCreationFailedError(APIException):
    """Exception raised when TOTP creation fails."""

    status_code = fastapi.status.HTTP_500_INTERNAL_SERVER_ERROR
    status = Status.FAILURE
    documentation_link = HTTPStatusDoc.HTTP_STATUS_500


class TotpRemovalFailedError(APIException):
    """Exception raised when TOTP removal fails."""

    status_code = fastapi.status.HTTP_500_INTERNAL_SERVER_ERROR
    status = Status.FAILURE
    documentation_link = HTTPStatusDoc.HTTP_STATUS_500


class TotpAlreadySetError(APIException):
    """Exception raised when attempting to set an already existing TOTP."""

    status_code = fastapi.status.HTTP_400_BAD_REQUEST
    status = Status.FAILURE
    documentation_link = HTTPStatusDoc.HTTP_STATUS_400


class TotpAttemptsIncriminationError(APIException):
    """Exception raised when TOTP verification attempts fails."""

    status_code = fastapi.status.HTTP_500_INTERNAL_SERVER_ERROR
    status = Status.FAILURE
    documentation_link = HTTPStatusDoc.HTTP_STATUS_500


class TotpVerificationAttemptsLimitError(APIException):
    """Exception raised when TOTP verification attempts reach the limit."""

    status_code = fastapi.status.HTTP_429_TOO_MANY_REQUESTS
    status = Status.FORBIDDEN
    documentation_link = HTTPStatusDoc.HTTP_STATUS_429
