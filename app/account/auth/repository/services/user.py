"""
Module for user service operations.

This module provides a service class for handling various user-related operations.
"""

import bcrypt
from fastapi.concurrency import run_in_threadpool
from sqlalchemy.ext.asyncio import AsyncSession, async_scoped_session

from app.account.auth.helpers.enums import AuthMessages
from app.account.auth.helpers.exceptions import UserInvalidCredentials
from app.account.auth.models import User
from app.account.auth.repository.bll.user import UserBusinessLogicLayer
from app.account.auth.schemas import UserRegisterInputSchema
from app.account.auth.schemas.user import UserAuthenticateInputSchema
from app.account.otp.helpers.exceptions import TotpVerificationFailedError
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
        self.user_bll = UserBusinessLogicLayer(user_dal=self.user_dal)

    async def register(
        self, user_input: UserRegisterInputSchema
    ) -> dict[str, User | Status | HTTPStatusDoc | AuthMessages]:
        """
        Register a new user.

        This method hashes the user's password and creates a new user record in the
        database. This method also set an otp for user. The user needs to verify itself
        through another method using the otp sent in this method.

        Parameters
        ----------
        user_input : UserRegisterInputSchema
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

        user = await self.user_bll.handle_register(
            user_input=user_input, hashed_password=hashed_password
        )
        await self.totp_service.set_totp(email=user.email)
        return {
            "status": Status.CREATED,
            "message": AuthMessages.SUCCESS_REGISTER_MESSAGE,
            "data": user,
            "documentation_link": HTTPStatusDoc.HTTP_STATUS_201,
        }

    async def verify_registration(
        self, email: str, totp: str
    ) -> dict[str, Status | HTTPStatusDoc | AuthMessages]:
        """
        Verify a user's account registration using OTP (TOTP).

        This method validates the provided OTP (TOTP) for the specified user.
        If the OTP is correct, the user's verification status is updated in the
        database.

        Parameters
        ----------
        email : str
            The email of the user attempting verification.
        totp : str
            The OTP (TOTP) provided by the user for verification.

        Returns
        -------
        dict[str, User | Status | HTTPStatusDoc | AuthMessages]
            A dictionary containing the status, a message, and an optional
            documentation link describing the result of the verification process.
        """
        user = await self.user_bll.get_user_for_registration_verification(email=email)

        otp_verification_result = await self.totp_service.verify_totp(
            email=user.email, totp=totp
        )
        if otp_verification_result.get("status") == Status.SUCCESS:
            await self.user_dal.verify_user(user_id=user.id)
            return {
                "status": Status.SUCCESS,
                "message": AuthMessages.SUCCESS_VERIFICATION,
                "documentation_link": HTTPStatusDoc.HTTP_STATUS_200,
            }

        return {
            "status": Status.FAILURE,
            "message": AuthMessages.FAILED_VERIFICATION,
            "documentation_link": HTTPStatusDoc.HTTP_STATUS_400,
        }

    async def authenticate(
        self, user_input: UserAuthenticateInputSchema
    ) -> dict[str, User | Status | HTTPStatusDoc | AuthMessages]:
        """
        Authenticate a user and initiate OTP (TOTP) setup.

        This method verifies the user's credentials, including email and password,
        and generates an OTP for further authentication steps. If the credentials
        are valid, the OTP is set for the user.

        Parameters
        ----------
        user_input : UserAuthenticateInputSchema
            An object containing the user's login details, including email and password.

        Returns
        -------
        dict[str, User | Status | HTTPStatusDoc | AuthMessages]
            A dictionary containing the login status, a message, the authenticated
            user's data, and an optional documentation link describing the result of the
            login process.

        Raises
        ------
        UserInvalidCredentials
            If the provided email or password is incorrect.
        """
        user = await self.user_dal.get_user_by_email(email=user_input.email)

        is_password_valid = self.check_password(
            password=user_input.password, hashed_password=user.hashed_password
        )
        if not is_password_valid:
            raise UserInvalidCredentials(AuthMessages.INVALID_CREDENTIALS.value)

        await self.totp_service.set_totp(email=user.email)
        return {
            "status": Status.SUCCESS,
            "message": AuthMessages.SUCCESS_LOGIN_MESSAGE,
            "data": user,
            "documentation_link": HTTPStatusDoc.HTTP_STATUS_200,
        }

    async def verify_authentication(self, email: str, totp: str) -> User:
        """
        Verify user authentication using email and TOTP.

        This method retrieves the user associated with the provided email,
        then verifies the provided TOTP against the user's record.

        Parameters
        ----------
        email : str
            The email of the user attempting authentication.
        totp : str
            The time-based one-time password provided for authentication.

        Returns
        -------
        User
            The authenticated user object if verification is successful.

        Raises
        ------
        TotpVerificationFailedError
            If TOTP verification fails.
        """
        # Get user from db though the user email.
        user = await self.user_dal.get_user_by_email(email=email)

        # Verify the provided totp.
        otp_verification_result = await self.totp_service.verify_totp(
            email=user.email, totp=totp
        )
        if otp_verification_result.get("status") == Status.SUCCESS:
            return user

        raise TotpVerificationFailedError("OTP verification failed. Please try again.")

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

    def check_password(self, password: str, hashed_password: str) -> bool:
        """
        Check if a plaintext password matches a hashed password.

        This method verifies the password by comparing it with its hashed counterpart
        using bcrypt.

        Parameters
        ----------
        password : str
            The plaintext password to verify.
        hashed_password : str
            The hashed password to compare against.

        Returns
        -------
        bool
            True if the password matches the hashed password, otherwise False.
        """
        is_valid = bcrypt.checkpw(
            password=password.encode("utf-8"),
            hashed_password=hashed_password.encode("utf-8"),
        )
        return is_valid
