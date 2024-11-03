"""Module defines exceptions related to OTPs."""


class OtpError(Exception):
    """Base exception for OTP-related errors."""


class TotpError(OtpError):
    """Base exception for TOTP-related errors."""


class TotpVerificationFailedError(TotpError):
    """Exception raised when TOTP verification fails."""


class TotpCreationFailedError(TotpError):
    """Exception raised when TOTP creation fails."""


class TotpRemovalFailedError(TotpError):
    """Exception raised when TOTP removal fails."""


class TotpAlreadySetError(TotpError):
    """Exception raised when attempting to set an already existing TOTP."""
