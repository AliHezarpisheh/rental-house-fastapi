"""Module defines enumeration constants for otp API response messages."""

from enum import StrEnum

from config.base import settings


class OtpMessages(StrEnum):
    """Enumeration of messages used in otp API responses."""

    OTP_SEND_SUCCESS = "Otp sent successfully"
    OTP_VERIFICATION_SUCCESS = "Otp verified successfully"
    OTP_CREATION_FAILED = "Otp creation failed. Check the logs!"
    OTP_VERIFICATION_FAILED = "Otp verification failed. Expired or not created"
    OTP_REMOVAL_FAILED = "Otp removal failed. Check the logs!"
    OTP_DATA_ERROR = "Error processing otp data. Check the logs!"
    OTP_TOO_MANY_REQUESTS = "Too many requests for verifying otp"
    OTP_ALREADY_ACTIVE = "User already has an active otp"
    OTP_SET_FAILED = "Failed to set OTP. Contact support"
    OTP_INCORRECT = "Incorrect OTP"
    EMAIL_INVALID = "Invalid email format"
    OTP_ONLY_DIGITS = "Otp must contain only digits"
    OTP_FIXED_DIGITS = f"Otp must be {settings.otp_digits} digits long"
