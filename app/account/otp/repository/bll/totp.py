import bcrypt
from redis.asyncio import Redis

from app.account.otp.helpers.exceptions import TotpAlreadySetException
from app.account.otp.repository.dal import TotpDataAccessLayer


class TOTPBusinessLogicLayer:
    def __init__(self, redis_client: Redis) -> None:
        self.redis_client = redis_client
        self.totp_dal = TotpDataAccessLayer(redis_client=self.redis_client)

    async def set_totp(self, user_id: int, hashed_totp: str) -> bool:
        is_totp_exist = await self.totp_dal.check_totp(user_id=user_id)
        if is_totp_exist:
            raise TotpAlreadySetException(
                "User has an active totp. Can not set multiple totp for a single user."
            )

        is_created = await self.totp_dal.set_totp(
            user_id=user_id, hashed_totp=hashed_totp
        )
        return is_created

    async def verify_totp(self, user_id: int, totp: str) -> bool:
        hashed_totp = await self.totp_dal.get_totp(user_id=user_id)
        is_verified = bcrypt.checkpw(totp.encode("utf-8"), hashed_totp.encode("utf-8"))
        if is_verified:
            await self.totp_dal.delete_totp(user_id=user_id)
        return is_verified
