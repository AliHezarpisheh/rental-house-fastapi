"""
Module containing the business logic layer for totp operations.

This module provides business logic methods for setting and verifying totp,
interfacing with the data access layer.
"""

import bcrypt
from fastapi.concurrency import run_in_threadpool
from redis.asyncio import Redis

from app.account.otp.helpers.enums import OtpMessages
from app.account.otp.helpers.exceptions import (
    TotpAlreadySetError,
    TotpVerificationAttemptsLimitError,
)
from app.account.otp.repository.dal import TotpDataAccessLayer
from config.base import logger


class TotpBusinessLogicLayer:
    """Business logic layer for TOTP-related operations."""

    MAX_VERIFY_ATTEMPTS = 5  # Every user can only attempt 5 times for verifying an totp

    def __init__(self, redis_client: Redis) -> None:
        """
        Initialize the `TotpBusinessLogicLayer`.

        Parameters
        ----------
        redis_client : Redis
            The Redis client for asynchronous operations.
        """
        self.redis_client = redis_client
        self.totp_dal = TotpDataAccessLayer(redis_client=self.redis_client)

    async def set_totp(self, email: str, hashed_totp: str) -> bool:
        """
        Set a new totp for a user, ensuring no existing active TOTP.

        Parameters
        ----------
        email : str
            The email of the user.
        hashed_totp : str
            The hashed TOTP value to be set.

        Returns
        -------
        bool
            True if the TOTP was successfully set, False otherwise.

        Raises
        ------
        TotpAlreadySetError
            If the user already has an active TOTP.
        """
        if await self.totp_dal.check_totp(email=email):
            logger.debug("Totp already set for email: %s", email)
            raise TotpAlreadySetError(OtpMessages.OTP_ALREADY_ACTIVE.value)

        return await self.totp_dal.set_totp(email=email, hashed_totp=hashed_totp)

    async def verify_totp(self, email: str, totp: str) -> bool:
        """
        Verify the totp for a user and delete it upon successful verification.

        This method also implement a rate limit for user totp verification. If the user
        attempts for verifying the totp reached a certain limit, an error will be
        raised, preventing user for further verification, preventing brute-force
        attacks.

        Parameters
        ----------
        email : str
            The email of the user.
        totp : str
            The totp provided by the user for verification.

        Returns
        -------
        bool
            True if the totp was successfully verified, False otherwise.
        """
        # Rate limit user totp verification.
        logger.debug("Checking user attempts for verifying totp, email: %s", email)

        user_attempts = await self.totp_dal.get_attempts(email=email)
        if user_attempts >= self.MAX_VERIFY_ATTEMPTS:
            raise TotpVerificationAttemptsLimitError(
                OtpMessages.OTP_TOO_MANY_REQUESTS.value
            )

        # Check totp hash and validate it.
        logger.debug("Verifying totp for email: %s", email)
        hashed_totp = await self.totp_dal.get_totp(email=email)

        # Increment user attempt for verifying the totp.
        await self.totp_dal.increment_attempts(email=email)

        # Verify the totp hash.
        is_verified = await run_in_threadpool(
            self._verify_totp, totp=totp, hashed_totp=hashed_totp
        )

        # If the user is verified, the totp should be deleted from the storage.
        if is_verified:
            logger.debug("Totp verified, deleting for email: %s", email)
            await self.totp_dal.delete_totp(email=email)
        return is_verified

    def hash_totp(self, totp: str) -> str:
        """
        Hash the totp using bcrypt.

        Parameters
        ----------
        totp : str
            The totp to be hashed.

        Returns
        -------
        str
            The hashed totp.
        """
        salt = bcrypt.gensalt()
        hashed_totp = bcrypt.hashpw(
            totp.encode("utf-8"),
            salt=salt,
        )
        return hashed_totp.decode("utf-8")

    def _verify_totp(self, totp: str, hashed_totp: str) -> bool:
        """
        Verify the hashed totp using bcrypt.

        Parameters
        ----------
        totp : str
            The totp got from user input to be verified.
        hashed_totp : str
            The hashed totp to be compared with user-input totp.

        Returns
        -------
        bool
            Wether or not the hashed of totp match the actual hashed totp.
        """
        return bcrypt.checkpw(totp.encode("utf-8"), hashed_totp.encode("utf-8"))
