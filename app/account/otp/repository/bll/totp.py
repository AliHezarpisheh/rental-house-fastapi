"""
Module containing the business logic layer for TOTP operations.

This module provides business logic methods for setting and verifying TOTPs,
interfacing with the data access layer.
"""

import bcrypt
from redis.asyncio import Redis

from app.account.otp.helpers.exceptions import (
    TotpAlreadySetError,
    TotpVerificationAttemptsLimitError,
)
from app.account.otp.repository.dal import TotpDataAccessLayer
from config.base import logger


class TOTPBusinessLogicLayer:
    """Business logic layer for TOTP-related operations."""

    MAX_VERIFY_ATTEMPTS = 5  # Every user can only attempt 5 times for verifying an OTP.

    def __init__(self, redis_client: Redis) -> None:
        """
        Initialize the `TOTPBusinessLogicLayer`.

        Parameters
        ----------
        redis_client : Redis
            The Redis client for asynchronous operations.
        """
        self.redis_client = redis_client
        self.totp_dal = TotpDataAccessLayer(redis_client=self.redis_client)

    async def set_totp(self, user_id: int, hashed_totp: str) -> bool:
        """
        Set a new TOTP for a user, ensuring no existing active TOTP.

        Parameters
        ----------
        user_id : int
            The ID of the user.
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
        if await self.totp_dal.check_totp(user_id=user_id):
            logger.debug("TOTP already set for user_id: %d", user_id)
            raise TotpAlreadySetError("User already has an active TOTP.")

        logger.debug("Setting new TOTP for user_id: %d", user_id)
        return await self.totp_dal.set_totp(user_id=user_id, hashed_totp=hashed_totp)

    async def verify_totp(self, user_id: int, totp: str) -> bool:
        """
        Verify the TOTP for a user and delete it upon successful verification.

        This method also implement a rate limit for user TOTP verification. If the user
        attempts for verifying the TOTP reached a certain limit, an error will be
        raised, preventing user for further verification, preventing brute-force
        attacks.

        Parameters
        ----------
        user_id : int
            The ID of the user.
        totp : str
            The TOTP provided by the user for verification.

        Returns
        -------
        bool
            True if the TOTP was successfully verified, False otherwise.
        """
        # Rate limit user OTP verification.
        logger.debug("Checking user attempts for verifying otp, user_id: %d", user_id)

        user_attempts = await self.totp_dal.get_attempts(user_id=user_id)
        if user_attempts >= self.MAX_VERIFY_ATTEMPTS:
            raise TotpVerificationAttemptsLimitError(
                "Too much requests for verifying OTP."
            )

        # Check OTP hash and validate it.
        logger.debug("Verifying TOTP for user_id: %d", user_id)

        hashed_totp = await self.totp_dal.get_totp(user_id=user_id)

        # Increment user attempt for verifying the OTP.
        await self.totp_dal.increment_attempts(user_id=user_id)

        # Verify the OTP hash.
        is_verified = bcrypt.checkpw(totp.encode("utf-8"), hashed_totp.encode("utf-8"))

        # If the user is verified, the OTP should be deleted from the storage.
        if is_verified:
            logger.debug("TOTP verified, deleting for user_id: %d", user_id)
            await self.totp_dal.delete_totp(user_id=user_id)
        return is_verified
