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
    TokenOutputSchema,
    UserAuthenticateInputSchema,
    UserOutputSchema,
    UserRegisterInputSchema,
)
from toolkit.api.enums import HTTPStatusDoc, OpenAPITags, Status
from toolkit.api.schemas.base import APIResponse

router = APIRouter(prefix="/users", tags=[OpenAPITags.USERS])


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=UserOutputSchema,
    response_model_exclude_none=True,
)
async def register(
    user_input: UserRegisterInputSchema,
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> dict[str, User | Status | HTTPStatusDoc | AuthMessages]:
    """
    Register a new user with the provided details.

    This endpoint accepts user details such as email and password,
    and creates a new user account.

    ### Parameters
    - **email**: The email address of the user, which must be valid.
    - **password**: A secure password for the user account.

    ### Notes
    The created account will be inactive and unverified. To activate and verify the
    account, the user must call the `/users/register/verify` endpoint.
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

    ### Parameters
    - **email**: The user's email address.
    - **totp**: A six-digit TOTP sent to the user's registered contact (e.g., email).

    ### Notes
    - The TOTP must be valid and within the defined time window.
    - Users need to provide the exact TOTP sent to their registered contact.
    """
    result = await user_service.verify_registration(email=email, totp=totp)
    return result


@router.post(
    "/authenticate",
    status_code=status.HTTP_201_CREATED,
    response_model=UserOutputSchema,
    response_model_exclude_none=True,
)
async def authenticate(
    user_input: UserAuthenticateInputSchema,
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> dict[str, User | Status | HTTPStatusDoc | AuthMessages]:
    """
    Authenticate a user through the user's credentials.

    This endpoint validates the user's credentials (e.g., email and password)
    and returns the user's profile information upon successful authentication. The token
    is accessible after verifying the auth, through sending the otp and verification of
    the otp.

    ### Parameters
    - **email**: The email address of the user, which must be valid.

    ### Notes
    **The authentication process is incomplete here**. To retrieve the access token
    required for accessing protected endpoints, the user must call the
    `/users/authenticate/verify` endpoint.
    """
    result = await user_service.authenticate(user_input=user_input)
    return result


@router.post(
    "/authenticate/verify",
    status_code=status.HTTP_200_OK,
    response_model=TokenOutputSchema,
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

    ### Parameters
    - **email**: The user's email address.
    - **totp**: A 6-digit TOTP used for verification.

    ### Notes
    - The response includes two keys: `access_token` and `type` (e.g., `"Bearer"`).
    - To authorize other endpoints in the Swagger UI:
    1. Copy the `type` and `access_token` values from the response.
    2. Combine them into a single string like: `Bearer eyJhbGciOiJI...`
    3. Click the **Authorize** button at the top-right.
    4. Paste the combined string into the input field and confirm.
    - This allows the Swagger UI to include the JWT in the `Authorization` header for
      secured endpoints.
    """
    user: User = await user_service.verify_authentication(email=email, totp=totp)
    token_data = token_service.grant_token(user=user)
    return token_data
