"""
Module containing repository data access layer for user related operations.

This module provides methods for interacting with the database to perform
CRUD operations on the user model.
"""

from __future__ import annotations

from typing import NoReturn

from sqlalchemy import insert, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, async_scoped_session

from app.account.auth.helpers.exceptions import (
    DuplicateUserError,
    UserDoesNotExistError,
)
from app.account.auth.models import User
from app.account.auth.schemas import UserInput
from config.base import logger


class UserDataAccessLayer:
    """Data access layer for user related operations."""

    def __init__(self, db_session: async_scoped_session[AsyncSession]) -> None:
        """
        Initialize the UserDataAccessLayer.

        Parameters
        ----------
        db_session : async_scoped_session[AsyncSession]
            The database session for asynchronous operations.
        """
        self.db_session = db_session

    async def create_user(self, user_input: UserInput, hashed_password: str) -> User:
        """
        Create a new user.

        Parameters
        ----------
        user_input : UserInput
            User data to create a new user.
        hashed_password : str
            Hashed password for the new user.

        Returns
        -------
        User
            The newly created user.
        """
        stmt = (
            insert(User)
            .values(
                username=user_input.username,
                email=user_input.email,
                hashed_password=hashed_password,
                is_active=True,
                is_verified=False,
            )
            .returning(User)
        )

        async with self.db_session.begin():
            try:
                result = await self.db_session.execute(stmt)
                user = result.scalar_one()
            except IntegrityError as exc:
                await self.db_session.rollback()
                self.handle_integrity_error(exc=exc)
        return user

    async def verify_user(self, user_id: int) -> None:
        """
        Verify a user by updating their verification status.

        Parameters
        ----------
        user_id : int
            The ID of the user to be verified.

        Raises
        ------
        UserDoesNotExistError
            If the user with the given ID does not exist in the database.
        """
        stmt = update(User).values(is_verified=True).where(User.id == user_id)

        async with self.db_session.begin():
            result = await self.db_session.execute(stmt)
            if result.rowcount == 0:
                raise UserDoesNotExistError("User does not exist.")

    @staticmethod
    def handle_integrity_error(exc: IntegrityError) -> NoReturn:
        """
        Handle integrity error.

        Raises
        ------
        DuplicateUserError
            If the error is due to a duplicate username or email.
        """
        if "duplicate key value violates unique constraint" in str(exc):
            if "account__auth__user_username_key" in str(exc):
                raise DuplicateUserError(
                    "User with this username already exists"
                ) from exc
            elif "account__auth__user_email_key" in str(exc):
                raise DuplicateUserError("User with this email already exists") from exc
        logger.warning("Unhandled Integrity error occurred. The error: %s", exc)
        raise exc
