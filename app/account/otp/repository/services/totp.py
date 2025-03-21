"""
Module for TOTP service operations.

This module provides a service class for handling various TOTP-related operations.
"""

import pyotp
from email_validator import EmailNotValidError, validate_email
from fastapi.concurrency import run_in_threadpool

from app.account.otp.helpers.enums import OtpMessages
from app.account.otp.helpers.exceptions import (
    TotpCreationFailedError,
    TotpVerificationFailedError,
)
from app.account.otp.repository.bll import TotpBusinessLogicLayer
from app.account.otp.repository.dal import TotpDataAccessLayer
from app.account.otp.tasks.email import send_otp_email
from config.base import logger, settings
from toolkit.api.enums import HTTPStatusDoc, Status
from toolkit.api.exceptions import ValidationError


class TotpService:
    """Service class for TOTP-related operations."""

    def __init__(
        self, totp_dal: TotpDataAccessLayer, totp_bll: TotpBusinessLogicLayer
    ) -> None:
        """
        Initialize the `TotpService`.

        Parameters
        ----------
        totp_dal : TotpDataAccessLayer
            The data access layer responsible for interacting with the data
            storage (e.g., Redis) to handle TOTP-related data.
        totp_bll : TotpBusinessLogicLayer
            The business logic layer responsible for the core TOTP operations, such as
            generating and validating TOTP codes.
        """
        self.totp_dal = totp_dal
        self.totp_bll = totp_bll

        self.totp = pyotp.TOTP(
            pyotp.random_base32(), interval=settings.otp_ttl, digits=settings.otp_digits
        )

    async def set_totp(self, email: str) -> dict[str, str]:
        """
        Set a new totp for the user.

        Parameters
        ----------
        email : str
            The email of the user for whom to set the totp.

        Returns
        -------
        dict[str, str]
            A dictionary containing the status, message, and documentation link.
        """
        self._validate_email(email=email)

        totp = self._generate_totp()
        hashed_totp = await run_in_threadpool(self.totp_bll.hash_totp, totp=totp)

        if await self.totp_bll.set_totp(email=email, hashed_totp=hashed_totp):
            send_otp_email.delay(to_email=email, otp=totp)
            logger.debug("Totp successfully send to email: %s", email)
            return {
                "status": Status.CREATED,
                "message": OtpMessages.OTP_SEND_SUCCESS,
                "documentation_link": HTTPStatusDoc.HTTP_STATUS_201,
            }

        raise TotpCreationFailedError(OtpMessages.OTP_CREATION_FAILED.value)

    async def verify_totp(self, email: str, totp: str) -> dict[str, str]:
        """
        Verify the totp for the user.

        Parameters
        ----------
        email : str
            The email of the user whose totp needs to be verified.
        totp : str
            The totp to be verified.

        Returns
        -------
        dict[str, str]
            A dictionary containing the status, message, and documentation link.
        """
        self._validate_email(email=email)
        self._validate_totp(totp=totp)

        if await self.totp_bll.verify_totp(email=email, totp=totp):
            return {
                "status": Status.SUCCESS,
                "message": OtpMessages.OTP_VERIFICATION_SUCCESS,
                "documentation_link": HTTPStatusDoc.HTTP_STATUS_200,
            }

        raise TotpVerificationFailedError(OtpMessages.OTP_VERIFICATION_FAILED.value)

    @staticmethod
    def _validate_email(email: str) -> None:
        try:
            validate_email(email)
        except EmailNotValidError:
            logger.debug("Invalid email provided: %s", email)
            raise ValidationError(OtpMessages.EMAIL_INVALID.value)

    @staticmethod
    def _validate_totp(totp: str) -> None:
        assert isinstance(totp, str), "totp should be instance of `str`"

        if not totp.isdigit():
            raise ValidationError(OtpMessages.OTP_ONLY_DIGITS.value)

        if len(totp) != settings.otp_digits:
            raise ValidationError(OtpMessages.OTP_FIXED_DIGITS.value)

    def _generate_totp(self) -> str:
        """
        Generate a new totp.

        Returns
        -------
        str
            A new otp string.
        """
        return self.totp.now()
