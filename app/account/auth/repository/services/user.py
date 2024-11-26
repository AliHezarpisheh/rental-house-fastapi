"""
Module for user service operations.

This module provides a service class for handling various user-related operations.
"""

import bcrypt
from fastapi.concurrency import run_in_threadpool
from sqlalchemy.ext.asyncio import AsyncSession, async_scoped_session

from app.account.auth.helpers.enums import AuthMessages
from app.account.auth.models import User
from app.account.auth.schemas import UserInput
from app.account.otp.repository.services import TotpService
from toolkit.api.enums import HTTPStatusDoc, Status

from ..dal import UserDataAccessLayer


class UserService:
    """Service class for user-related operations."""

    def __init__(
        self, db_session: async_scoped_session[AsyncSession], totp_service: TotpService
    ) -> None:
        """
        Initialize the UserService.

        Parameters
        ----------
        db_session : async_scoped_session[AsyncSession]
            The database session for asynchronous operations.
        """
        self.db_session = db_session
        self.totp_service = totp_service
        self.user_dal = UserDataAccessLayer(db_session=db_session)

    async def register(
        self, user_input: UserInput
    ) -> dict[str, User | Status | HTTPStatusDoc | AuthMessages]:
        """
        Register a new user.

        This method hashes the user's password and creates a new user record in the
        database. This method also set an otp for user. The user needs to verify itself
        through another method using the otp sent in this method.

        Parameters
        ----------
        user_input : UserInput
            The user input data required for registration.

        Returns
        -------
        dict[str, User | Status | HTTPStatusDoc | AuthMessages]
            The newly registered user as the data, plus other metadata related to the
            user registration.
        """
        # Perform password hashing in a separate thread, making event loop responsive
        hashed_password = await run_in_threadpool(
            self.hash_password, user_input.password
        )

        user = await self.user_dal.create_user(
            user_input=user_input, hashed_password=hashed_password
        )
        await self.totp_service.set_otp(user_id=user.id)
        return {
            "status": Status.CREATED,
            "message": AuthMessages.SUCCESS_REGISTER_MESSAGE,
            "data": user,
            "documentation_link": HTTPStatusDoc.HTTP_STATUS_201,
        }

    def hash_password(self, password: str) -> str:
        """
        Hash the user's password.

        This method generates a salt and hashes the password using bcrypt.

        Parameters
        ----------
        password : str
            The plaintext password to be hashed.

        Returns
        -------
        str
            The hashed password.
        """
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(
            password=password.encode("utf-8"),
            salt=salt,
        )
        return hashed_password.decode("utf-8")
