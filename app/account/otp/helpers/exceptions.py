"""Module defines exceptions related to OTPs."""

import fastapi

from toolkit.api.enums import HTTPStatusDoc, Status


class OtpError(Exception):
    """Base exception for OTP-related errors."""

    status_code = fastapi.status.HTTP_400_BAD_REQUEST
    status = Status.FAILURE
    http_status_doc = HTTPStatusDoc.HTTP_STATUS_400


class TotpError(OtpError):
    """Base exception for TOTP-related errors."""


class TotpVerificationFailedError(TotpError):
    """Exception raised when TOTP verification fails."""

    status_code = fastapi.status.HTTP_403_FORBIDDEN
    status = Status.FORBIDDEN
    http_status_doc = HTTPStatusDoc.HTTP_STATUS_403


class TotpCreationFailedError(TotpError):
    """Exception raised when TOTP creation fails."""


class TotpRemovalFailedError(TotpError):
    """Exception raised when TOTP removal fails."""


class TotpAlreadySetError(TotpError):
    """Exception raised when attempting to set an already existing TOTP."""


class TotpAttemptsIncriminationError(TotpError):
    """Exception raised when TOTP verification attempts fails."""

    status_code = fastapi.status.HTTP_500_INTERNAL_SERVER_ERROR
    status = Status.FAILURE
    http_status_doc = HTTPStatusDoc.HTTP_STATUS_500


class TotpVerificationAttemptsLimitError(TotpError):
    """Exception raised when TOTP verification attempts reach the limit."""

    status_code = fastapi.status.HTTP_429_TOO_MANY_REQUESTS
    status = Status.FORBIDDEN
    http_status_doc = HTTPStatusDoc.HTTP_STATUS_429
