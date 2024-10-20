"""
Module for TOTP service operations.

This module provides a service class for handling various TOTP-related operations.
"""

import bcrypt
import pyotp
from fastapi.concurrency import run_in_threadpool
from redis.asyncio import Redis

from app.account.otp.repository.bll import TOTPBusinessLogicLayer
from app.account.otp.repository.dal import TotpDataAccessLayer
from config.base import logger, settings
from toolkit.api.enums import HTTPStatusDoc, Status


class TotpService:
    """Service class for TOTP-related operations."""

    def __init__(self, redis_client: Redis):
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
        self.totp_bll = TOTPBusinessLogicLayer(redis_client=self.redis_client)

    async def set_otp(self, user_id: int) -> dict[str, str]:
        """
        Set a new OTP for the user.

        Parameters
        ----------
        user_id : int
            The ID of the user for whom to set the OTP.

        Returns
        -------
        dict[str, str]
            A dictionary containing the status, message, and documentation link.
        """
        totp = self._create_totp()
        hashed_totp = await run_in_threadpool(self._hash_totp, totp=totp)

        if await self.totp_bll.set_totp(user_id=user_id, hashed_totp=hashed_totp):
            logger.info("OTP successfully set for user_id: %d", user_id)
            return {
                "status": Status.CREATED,
                "message": "OTP sent successfully.",
                "documentation_link": HTTPStatusDoc.STATUS_201,
            }

        return {
            "status": Status.FAILURE,
            "message": "Failed to set OTP. Contact support.",
            "documentation_link": HTTPStatusDoc.STATUS_500,
        }

    async def verify_totp(self, user_id: int, totp: str) -> dict[str, str]:
        """
        Verify the OTP for the user.

        Parameters
        ----------
        user_id : int
            The ID of the user whose OTP needs to be verified.
        totp : str
            The OTP to be verified.

        Returns
        -------
        dict[str, str]
            A dictionary containing the status, message, and documentation link.
        """
        if await self.totp_bll.verify_totp(user_id=user_id, totp=totp):
            return {
                "status": Status.SUCCESS,
                "message": "OTP verified successfully.",
                "documentation_link": HTTPStatusDoc.STATUS_200,
            }

        return {
            "status": Status.FAILURE,
            "message": "OTP verification failed. Contact support.",
            "documentation_link": HTTPStatusDoc.STATUS_500,
        }

    def _create_totp(self) -> str:
        """
        Create a new TOTP.

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
