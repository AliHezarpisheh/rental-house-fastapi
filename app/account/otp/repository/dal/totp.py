"""
Module containing repository data access layer for TOTP related operations.

This module provides methods for interacting with the redis to perform set, get, check,
and unlink(delete) the otp keys and values.
"""

from __future__ import annotations

from typing import SupportsInt

import redis
from redis.asyncio import Redis

from app.account.otp.helpers.exceptions import (
    TotpAttemptsIncriminationError,
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
            "Attempting to set TOTP for user_id: %d, Redis key: %s",
            user_id,
            self._get_totp_key_name(user_id),
        )

        key_name = self._get_totp_key_name(user_id=user_id)
        mapping = self._get_totp_mapping(hashed_otp=hashed_totp)
        is_created: int = await self.redis_client.hset(  # type: ignore
            key_name,
            mapping=mapping,
        )
        await self.set_expiration(key_name, ttl=settings.otp_ttl)

        if not is_created:
            logger.error(
                "Failed to create TOTP for user_id: %d, Redis key: %s",
                user_id,
                key_name,
            )
            raise TotpCreationFailedError("OTP creation failed. Check the logs!")

        logger.debug("set_totp() - TOTP successfully created for user_id: %d", user_id)
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
        logger.debug("Retrieving TOTP for user_id: %d", user_id)

        key_name = self._get_totp_key_name(user_id=user_id)
        hashed_totp: str | None = await self.redis_client.hget(  # type: ignore
            key_name, "hashed_otp"
        )

        if not hashed_totp:
            logger.error(
                "No OTP found for user_id: %d, Redis key: %s",
                user_id,
                key_name,
            )
            raise TotpVerificationFailedError(
                "OTP verification failed. OTP expiration reached or no OTP was created."
            )

        logger.debug("Successfully retrieved TOTP for user_id: %d", user_id)
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
        logger.debug("Attempting to remove TOTP for user_id: %d", user_id)

        key_name = self._get_totp_key_name(user_id=user_id)
        is_deleted = await self.redis_client.unlink(key_name)

        if not is_deleted:
            logger.error("Failed to delete TOTP for user_id: %d", user_id)
            raise TotpRemovalFailedError("Server error! Call the support.")

        logger.debug("Successfully deleted TOTP for user_id: %d", user_id)
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
        logger.debug("Checking existence of TOTP for user_id: %d", user_id)

        key_name = self._get_totp_key_name(user_id=user_id)
        is_exist = await self.redis_client.exists(key_name)

        logger.debug(
            "TOTP existence for user_id: %d: %s",
            user_id,
            "Exists" if is_exist else "Does not exist",
        )
        return bool(is_exist)

    async def increment_attempts(self, user_id: int) -> None:
        """
        Increment the attempt counter for TOTP verification for a given user.

        This method increases the "attempts" field in the Redis hash for the
        specified user's TOTP data. It is used to track how many times a user
        has tried to verify their TOTP, supporting rate-limiting and preventing
        brute-force attacks.

        Parameters
        ----------
        user_id : int
            The ID of the user whose attempt counter will be incremented.

        Raises
        ------
        RedisError
            If the increment operation fails in Redis.
        """
        key_name = self._get_totp_key_name(user_id=user_id)
        try:
            await self.redis_client.hincrby(key_name, key="attempts")  # type: ignore
        except redis.exceptions.ResponseError as err:
            logger.error("Error while incrementing user attempts for the OTP: %s", err)
            raise TotpAttemptsIncriminationError(
                "Error while working with OTP data."
            ) from err

    async def get_attempts(self, user_id: int) -> int:
        """
        Retrieve the current number of TOTP verification attempts for a given user.

        This method fetches the "attempts" field in the Redis hash for the specified
        user TOTP data, allowing the application to check the current attempt count.

        Parameters
        ----------
        user_id : int
            The ID of the user whose attempt count will be retrieved.

        Returns
        -------
        int
            The number of verification attempts for the specified user. If the key
            is not existed, the method returns -1, indicating no keys are available.

        Raises
        ------
        RedisError
            If there is an error in retrieving the attempts from Redis.
        """
        key_name = self._get_totp_key_name(user_id=user_id)
        attempts: SupportsInt | None = await self.redis_client.hget(  # type: ignore
            key_name, key="attempts"
        )
        return int(attempts) if attempts is not None else -1

    async def set_expiration(self, key_name: str, ttl: int) -> None:
        """
        Set an expiration time for a specific Redis key associated with TOTP data.

        This method applies a time-to-live (TTL) on the Redis key to ensure the data
        is automatically removed after the specified duration, contributing to security
        and resource management.

        Parameters
        ----------
        key_name : str
            The name of the Redis key for which to set the expiration time.
        ttl : int
            The time-to-live duration (in seconds) for the key.

        Raises
        ------
        TotpCreationFailedError
            If setting the expiration fails in Redis.
        """
        is_set_expired = await self.redis_client.expire(key_name, time=ttl)
        if not is_set_expired:
            logger.error(
                "set_expiration () - Failed to set expiration time for Redis key: %s",
                key_name,
            )
            raise TotpCreationFailedError("OTP creation failed. Check the logs!")

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
        return f"totp:users:{user_id}"

    @staticmethod
    def _get_totp_mapping(hashed_otp: str) -> dict[str, str | int]:
        """
        Get the Redis hashmap for setting a hashed otp with attempts starting from 0.

        Parameters
        ----------
        hashed_totp : str
            The hashed TOTP value to be stored.

        Returns
        -------
        dict[str, str | int]
            A dictionary mapping to Redis hashmap. The dictionary contains the hashed
            otp and the user attempts for verifying the corresponding otp, starting from
            0.
        """
        return {"hashed_otp": hashed_otp, "attempts": 0}
