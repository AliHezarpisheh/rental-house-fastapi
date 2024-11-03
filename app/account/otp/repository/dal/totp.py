"""
Module containing repository data access layer for TOTP related operations.

This module provides methods for interacting with the redis to perform set, get, check,
and unlink(delete) the otp keys and values.
"""

from redis.asyncio import Redis

from app.account.otp.helpers.exceptions import (
    TotpCreationFailedError,
    TotpRemovalFailedError,
    TotpVerificationFailedError,
)
from config.base import logger, settings


class TotpDataAccessLayer:
    """Data access layer for TOTP related operations."""

    def __init__(self, redis_client: Redis):
        """
        Initialize the `TOTPDataAccessLayer`.

        Parameters
        ----------
        redis_client : Redis
            An asynchronous Redis client instance.
        """
        self.redis_client = redis_client

    async def set_totp(self, user_id: int, hashed_totp: str) -> bool:
        """
        Set a TOTP for a given user in Redis.

        Parameters
        ----------
        user_id : int
            The ID of the user.
        hashed_totp : str
            The hashed TOTP value to be stored.

        Returns
        -------
        bool
            True if the TOTP is successfully created, False otherwise.

        Raises
        ------
        TotpCreationFailedError
            If there is an error while creating the TOTP.
        """
        logger.debug(
            "set_totp() - Attempting to set TOTP for user_id: %d, Redis key: %s",
            user_id,
            self._get_totp_key_name(user_id),
        )

        key_name = self._get_totp_key_name(user_id=user_id)
        try:
            is_created = await self.redis_client.set(
                name=key_name, value=hashed_totp, ex=settings.otp_ttl
            )
        except Exception as err:
            logger.critical(
                "set_totp() - Exception occurred while setting TOTP for "
                "user_id: %d, error: %s",
                user_id,
                str(err),
                exc_info=True,
            )
            raise TotpCreationFailedError("Server error! Call the support.") from err

        if not is_created:
            logger.critical(
                "set_totp() - Failed to create TOTP for user_id: %d, Redis key: %s",
                user_id,
                key_name,
            )
            raise TotpCreationFailedError("Server error! Call the support.")

        logger.info("set_totp() - TOTP successfully created for user_id: %d", user_id)
        return bool(is_created)

    async def get_totp(self, user_id: int) -> str:
        """
        Retrieve the TOTP for a given user from Redis.

        Parameters
        ----------
        user_id : int
            The ID of the user.

        Returns
        -------
        str
            The hashed TOTP associated with the user.

        Raises
        ------
        TotpVerificationFailedError
            If there is an error retrieving or verifying the TOTP.
        """
        logger.debug("get_totp() - Retrieving TOTP for user_id: %d", user_id)

        key_name = self._get_totp_key_name(user_id=user_id)
        try:
            hashed_totp: str = await self.redis_client.get(name=key_name)
        except Exception as err:
            logger.error(
                "get_totp() - Exception occurred while getting TOTP for "
                "user_id: %d, error: %s",
                user_id,
                str(err),
                exc_info=True,
            )
            raise TotpVerificationFailedError(
                "Server error! Call the support."
            ) from err

        if not hashed_totp:
            logger.error(
                "get_totp() - No OTP found for user_id: %d, Redis key: %s",
                user_id,
                key_name,
            )
            raise TotpVerificationFailedError(
                "OTP verification failed. OTP expiration reached or no OTP was created."
            )

        logger.info("get_totp() - Successfully retrieved TOTP for user_id: %d", user_id)
        return hashed_totp

    async def delete_totp(self, user_id: int) -> bool:
        """
        Delete the TOTP for a given user from Redis.

        Parameters
        ----------
        user_id : int
            The ID of the user.

        Returns
        -------
        bool
            True if the TOTP is successfully deleted, False otherwise.

        Raises
        ------
        TotpRemovalFailedError
            If there is an error deleting the TOTP.
        """
        logger.debug(
            "delete_totp() - Attempting to remove TOTP for user_id: %d", user_id
        )

        key_name = self._get_totp_key_name(user_id=user_id)
        try:
            is_deleted = await self.redis_client.unlink(key_name)
        except Exception as err:
            logger.error(
                "delete_totp() - Exception occurred while deleting TOTP for "
                "user_id: %d, error: %s",
                user_id,
                str(err),
                exc_info=True,
            )
            raise TotpRemovalFailedError("Server error! Call the support.") from err

        if not is_deleted:
            logger.error(
                "delete_totp() - Failed to delete TOTP for user_id: %d", user_id
            )
            raise TotpRemovalFailedError("Server error! Call the support.")

        logger.info(
            "delete_totp() - Successfully deleted TOTP for user_id: %d", user_id
        )
        return bool(is_deleted)

    async def check_totp(self, user_id: int) -> bool:
        """
        Check if a TOTP exists for a given user in Redis.

        Parameters
        ----------
        user_id : int
            The ID of the user.

        Returns
        -------
        bool
            True if a TOTP exists for the user, False otherwise.
        """
        logger.debug(
            "check_totp() - Checking existence of TOTP for user_id: %d", user_id
        )

        key_name = self._get_totp_key_name(user_id=user_id)
        try:
            is_exist = await self.redis_client.exists(key_name)
        except Exception as err:
            logger.error(
                "check_totp() - Exception occurred while checking TOTP existence "
                "for user_id: %d, error: %s",
                user_id,
                str(err),
                exc_info=True,
            )
            return False

        logger.info(
            "check_totp() - TOTP existence for user_id: %d: %s",
            user_id,
            "Exists" if is_exist else "Does not exist",
        )
        return bool(is_exist)

    @staticmethod
    def _get_totp_key_name(user_id: int) -> str:
        """
        Get the Redis key name for the TOTP of a given user.

        Parameters
        ----------
        user_id : int
            The ID of the user.

        Returns
        -------
        str
            The key name used for storing the TOTP in Redis.
        """
        return f"totp:{user_id}"
