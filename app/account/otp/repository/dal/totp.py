from redis.asyncio import Redis

from app.account.otp.helpers.exceptions import (
    TotpCreationFailedException,
    TotpRemovalFailedException,
    TotpVerificationFailedException,
)
from config.base import logger, settings


class TotpDataAccessLayer:
    def __init__(self, redis_client: Redis):
        self.redis_client = redis_client

    async def set_totp(self, user_id: int, hashed_totp: str) -> bool:
        logger.debug("Attempting to set TOTP for user Id: %d", user_id)

        key_name = self._get_totp_key_name(user_id=user_id)
        is_created = await self.redis_client.set(
            name=key_name, value=hashed_totp, ex=settings.otp_ttl
        )
        if not is_created:
            logger.critical(
                "Failed to create TOTP for user ID: %d, Redis key: %s",
                user_id,
                key_name,
            )
            raise TotpCreationFailedException("Server error! Call the support.")

        logger.info("TOTP successfully created for user ID: %d", user_id)
        return is_created

    async def get_totp(self, user_id: int) -> str:
        logger.debug("Getting totp token for user: (ID) %d", user_id)

        key_name = self._get_totp_key_name(user_id=user_id)
        hashed_totp = await self.redis_client.get(name=key_name)
        if not hashed_totp:
            logger.error("No otp is dedicated for the user: (ID) %d", user_id)
            raise TotpVerificationFailedException(
                "OTP verification failed. "
                "OTP expire time reached or no OTP was created."
            )

        logger.info("Successfully get totp for user: (ID) %d", user_id)
        return hashed_totp

    async def delete_totp(self, user_id: int) -> bool:
        logger.debug("Removing totp token for user: (ID) %d", user_id)

        key_name = self._get_totp_key_name(user_id=user_id)
        is_deleted = await self.redis_client.unlink(key_name)
        if not is_deleted:
            logger.error("Could not delete otp for user: (ID) %d", user_id)
            raise TotpRemovalFailedException("Server error! Call the support.")

        logger.info("Successfully deleted totp for user: (ID) %d", user_id)
        return is_deleted

    async def check_totp(self, user_id: int) -> bool:
        logger.debug("Checking existence of totp for user: (ID) %d", user_id)

        key_name = self._get_totp_key_name(user_id=user_id)
        is_exist = await self.redis_client.exists(key_name)
        return bool(is_exist)

    @staticmethod
    def _get_totp_key_name(user_id: int) -> str:
        return f"totp:{user_id}"
