"""
Module containing repository data access layer for TOTP related operations.

This module provides methods for interacting with the redis to perform set, get, check,
and unlink(delete) the otp keys and values.
"""

from __future__ import annotations

from typing import SupportsInt

import redis
from redis.asyncio import Redis
from redis.asyncio.client import Pipeline

from app.account.otp.helpers.enums import OtpMessages
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

    async def set_totp(self, email: str, hashed_totp: str) -> bool:
        """
        Set a TOTP for a given user email in Redis.

        Parameters
        ----------
        email : str
            The email of the user.
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
        key_name = self._get_totp_key_name(email=email)
        logger.debug(
            "Attempting to set totp for email: %s, Redis key: %s",
            email,
            key_name,
        )
        mapping = self._get_totp_mapping(hashed_totp=hashed_totp)

        redis_pipeline = self.redis_client.pipeline()
        await redis_pipeline.hset(  # type: ignore
            key_name,
            mapping=mapping,
        )
        await self.set_expiration(
            key_name, ttl=settings.otp_ttl, pipeline=redis_pipeline
        )
        is_created, _ = await redis_pipeline.execute()

        if not is_created:
            logger.error(
                "Failed to create totp for email: %s, Redis key: %s",
                email,
                key_name,
            )
            raise TotpCreationFailedError(OtpMessages.OTP_CREATION_FAILED.value)

        logger.debug("TOTP successfully created for email: %s", email)
        return bool(is_created)

    async def get_totp(self, email: str) -> str:
        """
        Retrieve the TOTP for a given user email from Redis.

        Parameters
        ----------
        email : str
            The email of the user.

        Returns
        -------
        str
            The hashed TOTP associated with the user.

        Raises
        ------
        TotpVerificationFailedError
            If there is an error retrieving or verifying the TOTP.
        """
        logger.debug("Retrieving top for email: %s", email)

        key_name = self._get_totp_key_name(email=email)
        hashed_totp: str | None = await self.redis_client.hget(  # type: ignore
            key_name, "hashed_totp"
        )

        if not hashed_totp:
            logger.error(
                "No TOTP found for email: %s, Redis key: %s",
                email,
                key_name,
            )
            raise TotpVerificationFailedError(OtpMessages.OTP_VERIFICATION_FAILED.value)

        logger.debug("Successfully retrieved TOTP for email: %s", email)
        return hashed_totp

    async def delete_totp(self, email: str) -> bool:
        """
        Delete the TOTP for a given user email from Redis.

        Parameters
        ----------
        email : str
            The email of the user.

        Returns
        -------
        bool
            True if the TOTP is successfully deleted, False otherwise.

        Raises
        ------
        TotpRemovalFailedError
            If there is an error deleting the TOTP.
        """
        logger.debug("Attempting to remove totp for email: %s", email)

        key_name = self._get_totp_key_name(email=email)
        is_deleted = await self.redis_client.unlink(key_name)

        if not is_deleted:
            logger.error("Failed to delete totp for email: %s", email)
            raise TotpRemovalFailedError(OtpMessages.OTP_REMOVAL_FAILED.value)

        logger.debug("Successfully deleted TOTP for email: %s", email)
        return bool(is_deleted)

    async def check_totp(self, email: str) -> bool:
        """
        Check if a TOTP exists for a given user in Redis.

        Parameters
        ----------
        email : str
            The ID of the user.

        Returns
        -------
        bool
            True if a TOTP exists for the user, False otherwise.
        """
        logger.debug("Checking existence of TOTP for email: %s", email)

        key_name = self._get_totp_key_name(email=email)
        is_exist = await self.redis_client.exists(key_name)

        logger.debug(
            "TOTP existence for email: %s: %s",
            email,
            "Exists" if is_exist else "Does not exist",
        )
        return bool(is_exist)

    async def increment_attempts(self, email: str) -> None:
        """
        Increment the attempt counter for totp verification for a given user.

        This method increases the "attempts" field in the Redis hash for the
        specified user's totp data. It is used to track how many times a user
        has tried to verify their totp, supporting rate-limiting and preventing
        brute-force attacks.

        Parameters
        ----------
        email : str
            The email of the user whose attempt counter will be incremented.

        Raises
        ------
        RedisError
            If the increment operation fails in Redis.
        """
        key_name = self._get_totp_key_name(email=email)
        try:
            await self.redis_client.hincrby(key_name, key="attempts")  # type: ignore
        except redis.exceptions.ResponseError as err:
            logger.error("Error while incrementing user attempts for the OTP: %s", err)
            raise TotpAttemptsIncriminationError(
                OtpMessages.OTP_DATA_ERROR.value
            ) from err

    async def get_attempts(self, email: str) -> int:
        """
        Retrieve the current number of TOTP verification attempts for a given user.

        This method fetches the "attempts" field in the Redis hash for the specified
        user TOTP data, allowing the application to check the current attempt count.

        Parameters
        ----------
        email : str
            The email of the user whose attempt count will be retrieved.

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
        key_name = self._get_totp_key_name(email=email)
        attempts: SupportsInt | None = await self.redis_client.hget(  # type: ignore
            key_name, key="attempts"
        )
        return int(attempts) if attempts is not None else -1

    async def set_expiration(
        self, key_name: str, ttl: int, pipeline: Pipeline | None = None
    ) -> None:
        """
        Set an expiration time for a specific Redis key associated with totp data.

        This method applies a time-to-live (TTL) on the Redis key to ensure the data
        is automatically removed after the specified duration, contributing to security
        and resource management.

        Parameters
        ----------
        key_name : str
            The name of the Redis key for which to set the expiration time.
        ttl : int
            The time-to-live duration (in seconds) for the key.
        pipeline : Pipeline, optional
            The redis pipeline object, reducing application roundtrip to redis server.
            If not provided, the redis_client attached to class will be used.

        Raises
        ------
        TotpCreationFailedError
            If setting the expiration fails in Redis.
        """
        client = pipeline if pipeline else self.redis_client
        is_set_expired = await client.expire(key_name, time=ttl)
        if not is_set_expired:
            logger.error(
                "Failed to set expiration time for Redis key: %s",
                key_name,
            )
            raise TotpCreationFailedError(OtpMessages.OTP_CREATION_FAILED.value)

    @staticmethod
    def _get_totp_key_name(email: str) -> str:
        """
        Get the Redis key name for the TOTP of a given user.

        Parameters
        ----------
        email : str
            The ID of the user.

        Returns
        -------
        str
            The key name used for storing the TOTP in Redis.
        """
        return f"totp:users:{email}"

    @staticmethod
    def _get_totp_mapping(hashed_totp: str) -> dict[str, str | int]:
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
        return {"hashed_totp": hashed_totp, "attempts": 0}
