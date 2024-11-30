"""Module defines routers related to users."""

from typing import Annotated

from fastapi import APIRouter, Body, Depends, status
from pydantic import BeforeValidator, EmailStr

from app.account.auth.api.dependencies.services import (
    get_token_service,
    get_user_service,
)
from app.account.auth.helpers.enums import AuthMessages
from app.account.auth.models import User
from app.account.auth.repository.services import TokenService, UserService
from app.account.auth.schemas import (
    TokenOutput,
    UserAuthenticateInput,
    UserOutput,
    UserRegisterInput,
)
from toolkit.api.enums import HTTPStatusDoc, OpenAPITags, Status
from toolkit.api.schemas.base import APIResponse

router = APIRouter(prefix="/users", tags=[OpenAPITags.USERS])


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=UserOutput,
    response_model_exclude_none=True,
)
async def register(
    user_input: UserRegisterInput,
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> dict[str, User | Status | HTTPStatusDoc | AuthMessages]:
    """
    Register a new user with the provided details.

    This endpoint accepts user details such as username, email, and password,
    and creates a new user account. The created account will be inactive and
    unverified. To activate and verify the account, the user must call the
    `/users/{user_id}/verify` endpoint.

    - **username**: Unique identifier for the user.
    - **email**: The email address of the user, which must be valid.
    - **password**: A secure password for the user account.
    \f
    Parameters
    ----------
    user_input : UserRegisterInput
        A Pydantic schema containing the user's registration data.
    user_service : UserService
        A service dependency for handling user operations.

    Returns
    -------
    dict
        A dictionary containing the status, message, documentation link,
        and user data if registration is successful.

    Notes
    -----
    This endpoint only registers the user. Verification is required
    via the `/users/{user_id}/verify` endpoint.
    """
    result = await user_service.register(user_input=user_input)
    return result


@router.post(
    "/register/verify",
    status_code=status.HTTP_200_OK,
    response_model=APIResponse,
    response_model_exclude_none=True,
)
async def verify_user_registration(
    email: Annotated[EmailStr, Body(embed=True, examples=["test@gmail.com"])],
    totp: Annotated[
        str, Body(embed=True, examples=["213957", 235092]), BeforeValidator(str)
    ],
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> dict[str, Status | HTTPStatusDoc | AuthMessages]:
    """
    Verify a user's account registration using a Time-based One-Time Password (TOTP).

    This endpoint completes the user registration process by verifying
    the user's account with the provided TOTP. Once verified, the user
    can access their account and associated services.

    - **email**: The user's email address.
    - **totp**: A six-digit TOTP sent to the user's registered contact (e.g., email).

    \f
    Parameters
    ----------
    email : EmailStr
        The email address of the user requesting verification.
    totp : str
        The Time-based One-Time Password (TOTP) provided by the user.
    user_service : UserService
        A service dependency for handling user verification operations.

    Returns
    -------
    dict
        A dictionary containing the status, message, and documentation link,
        indicating the success or failure of the verification process.

    Notes
    -----
    - The TOTP must be valid and within the defined time window.
    - Users need to provide the exact TOTP sent to their registered contact.
    """
    result = await user_service.verify_registration(email=email, totp=totp)
    return result


@router.post(
    "/authenticate",
    status_code=status.HTTP_200_OK,
    response_model=UserOutput,
    response_model_exclude_none=True,
)
async def authenticate(
    user_input: UserAuthenticateInput,
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> dict[str, User | Status | HTTPStatusDoc | AuthMessages]:
    """
    Authenticate a user through the user's credentials.

    This endpoint validates the user's credentials (e.g., email and password)
    and returns the user's profile information upon successful authentication. The token
    is accessible after verifying the auth, through sending the otp and verification of
    the otp.

    - **username**: Unique identifier for the user.
    - **email**: The email address of the user, which must be valid.

    \f
    Parameters
    ----------
    user_input : UserAuthenticateInput
        The input data containing the user's credentials.
    user_service : UserService
        A service dependency for performing user authentication.

    Returns
    -------
    dict
        A dictionary containing the authenticated user's data, along with
        status, message, and optional documentation links.

    Notes
    -----
    - The credentials are validated against stored user data.
    - If authentication fails, an appropriate error message will be returned.
    - Upon successful login, the user has to verify the auth through otp verification.
    """
    result = await user_service.authenticate(user_input=user_input)
    return result


@router.post(
    "/authenticate/verify",
    status_code=status.HTTP_200_OK,
    response_model=TokenOutput,
    response_model_exclude_none=True,
)
async def verify_login(
    email: Annotated[EmailStr, Body(embed=True, examples=["test@gmail.com"])],
    totp: Annotated[
        str, Body(embed=True, examples=["213957", 235092]), BeforeValidator(str)
    ],
    user_service: Annotated[UserService, Depends(get_user_service)],
    token_service: Annotated[TokenService, Depends(get_token_service)],
) -> dict[str, str]:
    """
    Verify a user's authentication and issue an access token.

    This endpoint verifies the user's identity using their email and a Time-based
    One-Time Password (TOTP). Upon successful verification, it grants the user an
    access token for subsequent authenticated requests.

    - **email**: The user's email address.
    - **totp**: A 6-digit TOTP used for verification.

    \f
    Parameters
    ----------
    email : EmailStr
        The email address of the user requesting verification.
    totp : str
        The Time-based One-Time Password provided by the user.
    user_service : UserService
        Service used to perform authentication checks for the user.
    token_service : TokenService
        Service used to issue access tokens upon successful authentication.

    Returns
    -------
    dict[str, str]
        A dictionary containing:
        - `access_token`: The access token for the user.
        - `type`: The token type (e.g., "Bearer").

    Notes
    -----
    - The `verify_authentication` method checks the email and TOTP against stored
      user data and current OTP validity.
    - The `grant_token` method generates an access token for the user upon successful
      authentication.
    - This endpoint is part of a multi-step authentication process and ensures that
      only verified users are granted access tokens.
    """
    user: User = await user_service.verify_authentication(email=email, totp=totp)
    token_data = token_service.grant_token(user=user)
    return token_data
