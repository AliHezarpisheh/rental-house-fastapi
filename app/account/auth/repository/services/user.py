"""
Module for user service operations.

This module provides a service class for handling various user-related operations.
"""

import bcrypt
from fastapi.concurrency import run_in_threadpool
from sqlalchemy.ext.asyncio import AsyncSession, async_scoped_session

from app.account.auth.models import User
from app.account.auth.schemas import UserInput

from ..dal import UserDataAccessLayer


class UserService:
    """Service class for user-related operations."""

    def __init__(self, db_session: async_scoped_session[AsyncSession]) -> None:
        """
        Initialize the UserService.

        Parameters
        ----------
        db_session : async_scoped_session[AsyncSession]
            The database session for asynchronous operations.
        """
        self.db_session = db_session
        self.user_dal = UserDataAccessLayer(db_session=db_session)

    async def register(self, user_input: UserInput) -> User:
        """
        Register a new user.

        This method hashes the user's password and creates a new user record in the
        database.

        Parameters
        ----------
        user_input : UserInput
            The user input data required for registration.

        Returns
        -------
        User
            The newly registered user.
        """
        # Perform password hashing in a separate thread, making event loop responsive
        hashed_password = await run_in_threadpool(
            self.hash_password, user_input.password
        )
        user = await self.user_dal.create_user(
            user_input=user_input, hashed_password=hashed_password
        )
        return user

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
