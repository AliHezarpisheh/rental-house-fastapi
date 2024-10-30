"""Module defines exceptions related to OTPs."""


class OtpException(Exception):
    """Base exception for OTP-related errors."""


class TotpException(OtpException):
    """Base exception for TOTP-related errors."""


class TotpVerificationFailedException(TotpException):
    """Exception raised when TOTP verification fails."""


class TotpCreationFailedException(TotpException):
    """Exception raised when TOTP creation fails."""


class TotpRemovalFailedException(TotpException):
    """Exception raised when TOTP removal fails."""


class TotpAlreadySetException(TotpException):
    """Exception raised when attempting to set an already existing TOTP."""
