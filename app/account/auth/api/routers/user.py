"""Module defines routers related to users."""

from typing import Annotated

from fastapi import APIRouter, Body, Depends, Path, status
from pydantic import BeforeValidator

from app.account.auth.api.dependencies.services import get_user_service
from app.account.auth.helpers.enums import AuthMessages
from app.account.auth.models import User
from app.account.auth.repository.services import UserService
from app.account.auth.schemas import UserOutput, UserRegisterInput
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
    "/{user_id}/verify",
    status_code=status.HTTP_200_OK,
    response_model=APIResponse,
    response_model_exclude_none=True,
)
async def verify_user(
    user_id: Annotated[int, Path()],
    totp: Annotated[
        str, Body(embed=True, examples=["213957", 235092]), BeforeValidator(str)
    ],
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> dict[str, User | Status | HTTPStatusDoc | AuthMessages]:
    """
    Verify a user's account using a Time-based One-Time Password (TOTP).

    This endpoint completes the user registration process by verifying
    the user's account with the provided TOTP. Once verified, the user
    can access their account and associated services.

    - **user_id**: The unique identifier of the user to be verified.
    - **totp**: A six-digit TOTP sent to the user's registered contact (e.g., email).

    \f
    Parameters
    ----------
    user_id : int
        The unique identifier of the user to be verified.
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
    result = await user_service.verify(user_id=user_id, totp=totp)
    return result
