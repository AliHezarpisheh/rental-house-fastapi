"""Define enumeration constants for auth API response messages."""

from enum import StrEnum


class AuthMessages(StrEnum):
    """Enumeration of messages used in auth API responses."""

    SUCCESS_REGISTER_MESSAGE = (
        "Registration successful. Otp has been sent to your email for verification."
    )
    SUCCESS_LOGIN_MESSAGE = (
        "Login successful. Otp has been sent to your email for verification."
    )
    SUCCESS_VERIFICATION = "Your account has been verified successfully!"
    FAILED_VERIFICATION = "Invalid or expired otp. Please try again."
    INVALID_CREDENTIALS = "Invalid email or password."
    TOKEN_EXPIRATION = "Token has expired. Please log in again to obtain a new token."
    UNAUTHORIZED_MESSAGE = (
        "Token is not valid. Please log in again to obtain a new token."
    )
    EMAIL_ALREADY_TAKEN = "This email has been already taken"
    ALREADY_VERIFIED = "The user has been already verified"
    USER_NOT_EXIST = "User does not exists"
