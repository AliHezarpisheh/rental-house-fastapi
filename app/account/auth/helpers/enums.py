"""Define enumeration constants for auth API response messages."""

from enum import StrEnum


class AuthMessages(StrEnum):
    """Enumeration of messages used in auth API responses."""

    SUCCESS_REGISTER_MESSAGE = (
        "Registration successful. OTP has been sent to your email for verification."
    )
    SUCCESS_LOGIN_MESSAGE = (
        "Login successful. OTP has been sent to your email for verification."
    )
    SUCCESS_VERIFICATION = "Your account has been verified successfully!"
    FAILED_VERIFICATION = "Invalid or expired OTP. Please try again."
    INVALID_CREDENTIALS = "Invalid email or password."
    TOKEN_EXPIRATION = "Token has expired. Please log in again to obtain a new token."
    UNAUTHORIZED_MESSAGE = (
        "Token is not valid. Please log in again to obtain a new token."
    )
    INTERNAL_TOKEN_ERROR = (
        "Internal error generating token. Check the logs for more info."
    )
