"""
Module containing the business logic layer for user-related operations.

This module provides business logic methods for registration and authentication of
users, interfacing with the data access layer.
"""

from __future__ import annotations

from app.account.auth.helpers.enums import AuthMessages
from app.account.auth.helpers.exceptions import (
    UserAlreadyRegisteredError,
    UserAlreadyVerified,
    UserDoesNotExistError,
)
from app.account.auth.models.user import User
from app.account.auth.repository.dal.user import UserDataAccessLayer
from app.account.auth.schemas.user import UserRegisterInputSchema


class UserBusinessLogicLayer:
    """Business logic layer for user-related operations."""

    def __init__(self, user_dal: UserDataAccessLayer) -> None:
        """
        Initialize the `UserBusinessLogicLayer`.

        Parameters
        ----------
        user_dal : UserDataAccessLayer
            The data access layer responsible for interacting with the data
            storage to handle user-related data.
        """
        self.user_dal = user_dal

    async def handle_register(
        self, user_input: UserRegisterInputSchema, hashed_password: str
    ) -> User:
        """
        Handle the user registration.

        Handle user registration by checking if the user already exists and creating
        a new user if necessary.

        Parameters
        ----------
        user_input : UserRegisterInputSchema
            The input data containing user registration details.
        hashed_password : str
            The hashed password of the user.

        Returns
        -------
        User
            The newly created or existing user object, depending on whether the
            user was already registered.

        Raises
        ------
        UserAlreadyRegisteredError
            If the user is already registered and verified.
        """
        try:
            user = await self.user_dal.get_user_by_email(email=user_input.email)
            if user.is_verified:
                raise UserAlreadyRegisteredError(AuthMessages.EMAIL_ALREADY_TAKEN.value)
            return user
        except UserDoesNotExistError:
            user = await self.user_dal.create_user(
                user_input=user_input,
                hashed_password=hashed_password,
                is_active=True,
                is_verified=False,
            )
            return user

    async def get_user_for_registration_verification(self, email: str) -> User:
        """
        Get user for registration verification.

        Retrieve a user for registration verification by checking if the user's email
        exists and if they are not already verified.

        Parameters
        ----------
        email : str
            The email address of the user to be verified.

        Returns
        -------
        User
            The user object associated with the provided email.

        Raises
        ------
        UserAlreadyVerified
            If the user is already verified.
        """
        user = await self.user_dal.get_user_by_email(email=email, is_active=True)
        if user.is_verified:
            raise UserAlreadyVerified(AuthMessages.ALREADY_VERIFIED.value)
        return user
