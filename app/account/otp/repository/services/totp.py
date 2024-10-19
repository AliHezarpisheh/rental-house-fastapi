import bcrypt
import pyotp
from fastapi.concurrency import run_in_threadpool
from redis.asyncio import Redis

from app.account.otp.repository.bll import TOTPBusinessLogicLayer
from app.account.otp.repository.dal import TotpDataAccessLayer
from config.base import logger, settings
from toolkit.api.enums import HTTPStatusDoc, Status


class TotpService:
    def __init__(self, redis_client: Redis):
        self.redis_client = redis_client
        self.totp = pyotp.TOTP(
            pyotp.random_base32(), interval=settings.otp_ttl, digits=settings.otp_digits
        )

        self.totp_dal = TotpDataAccessLayer(redis_client=self.redis_client)
        self.totp_bll = TOTPBusinessLogicLayer(redis_client=self.redis_client)

    async def set_otp(self, user_id: int) -> dict[str, str]:
        totp = self._create_totp()
        hashed_totp = await run_in_threadpool(self._hash_totp, totp=totp)
        is_totp_created = await self.totp_bll.set_totp(
            user_id=user_id, hashed_totp=hashed_totp
        )
        if is_totp_created:
            logger.info("Successfully set the otp for user: (Id) %d", user_id)
            return {
                "status": Status.CREATED,
                "message": "OTP sent successfully.",
                "documentation_link": HTTPStatusDoc.STATUS_201,
            }
        logger.error(
            "Unknown failure reason for setting totp, redis response: %s",
            is_totp_created,
        )
        return {
            "status": Status.FAILURE,
            "message": "Something went wrong, call the support.",
            "documentation_link": HTTPStatusDoc.STATUS_500,
        }

    async def verify_totp(self, user_id: int, totp: str) -> dict[str, str]:
        is_verified = await self.totp_bll.verify_totp(user_id=user_id, totp=totp)
        if is_verified:
            return {
                "status": Status.SUCCESS,
                "message": "OTP verified successfully.",
                "documentation_link": HTTPStatusDoc.STATUS_200,
            }
        return {
            "status": Status.FAILURE,
            "message": "Something went wrong, call the support.",
            "documentation_link": HTTPStatusDoc.STATUS_500,
        }

    def _create_totp(self) -> str:
        return self.totp.now()

    def _hash_totp(self, totp: str) -> str:
        salt = bcrypt.gensalt()
        hashed_otp = bcrypt.hashpw(
            totp.encode("utf-8"),
            salt=salt,
        )
        return hashed_otp.decode("utf-8")
