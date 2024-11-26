"""Define enumeration constants for auth API response messages."""

from enum import StrEnum


class AuthMessages(StrEnum):
    """Enumeration of messages used in auth API responses."""

    SUCCESS_REGISTER_MESSAGE = (
        "Registration successful. OTP has been sent to your email for verification."
    )
    SUCCESS_VERIFICATION = "Your account has been verified successfully!"
    FAILED_VERIFICATION = "Invalid or expired OTP. Please try again."
