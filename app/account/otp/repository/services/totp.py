"""
Module for TOTP service operations.

This module provides a service class for handling various TOTP-related operations.
"""

import bcrypt
import pyotp
from fastapi.concurrency import run_in_threadpool
from redis.asyncio import Redis

from app.account.otp.helpers.exceptions import TotpVerificationFailedError
from app.account.otp.repository.bll import TotpBusinessLogicLayer
from app.account.otp.repository.dal import TotpDataAccessLayer
from config.base import logger, settings
from toolkit.api.enums import HTTPStatusDoc, Status


class TotpService:
    """Service class for TOTP-related operations."""

    def __init__(self, redis_client: Redis) -> None:
        """
        Initialize the `TotpService`.

        Parameters
        ----------
        redis_client : Redis
            An asynchronous Redis client instance.
        """
        self.redis_client = redis_client
        self.totp = pyotp.TOTP(
            pyotp.random_base32(), interval=settings.otp_ttl, digits=settings.otp_digits
        )
        self.totp_dal = TotpDataAccessLayer(redis_client=self.redis_client)
        self.totp_bll = TotpBusinessLogicLayer(redis_client=self.redis_client)

    async def set_totp(self, email: str) -> dict[str, str]:
        """
        Set a new TOTP for the user.

        Parameters
        ----------
        email : str
            The email of the user for whom to set the OTP.

        Returns
        -------
        dict[str, str]
            A dictionary containing the status, message, and documentation link.
        """
        totp = self._generate_totp()
        hashed_totp = await run_in_threadpool(self._hash_totp, totp=totp)

        if await self.totp_bll.set_totp(email=email, hashed_totp=hashed_totp):
            logger.info("OTP successfully set for email: %s", email)
            return {
                "status": Status.CREATED,
                "message": "TOTP sent successfully.",
                "documentation_link": HTTPStatusDoc.HTTP_STATUS_201,
            }

        return {
            "status": Status.FAILURE,
            "message": "Failed to set TOTP. Contact support.",
            "documentation_link": HTTPStatusDoc.HTTP_STATUS_500,
        }

    async def verify_totp(self, email: str, totp: str) -> dict[str, str]:
        """
        Verify the TOTP for the user.

        Parameters
        ----------
        email : str
            The email of the user whose TOTP needs to be verified.
        totp : str
            The TOTP to be verified.

        Returns
        -------
        dict[str, str]
            A dictionary containing the status, message, and documentation link.
        """
        if await self.totp_bll.verify_totp(email=email, totp=totp):
            return {
                "status": Status.SUCCESS,
                "message": "TOTP verified successfully.",
                "documentation_link": HTTPStatusDoc.HTTP_STATUS_201,
            }

        raise TotpVerificationFailedError("Incorrect OTP.")

    def _generate_totp(self) -> str:
        """
        Generate a new TOTP.

        Returns
        -------
        str
            A new TOTP string.
        """
        return self.totp.now()

    def _hash_totp(self, totp: str) -> str:
        """
        Hash the TOTP using bcrypt.

        Parameters
        ----------
        totp : str
            The TOTP to be hashed.

        Returns
        -------
        str
            The hashed TOTP.
        """
        salt = bcrypt.gensalt()
        hashed_otp = bcrypt.hashpw(
            totp.encode("utf-8"),
            salt=salt,
        )
        return hashed_otp.decode("utf-8")
