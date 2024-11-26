"""Module defines routers related to users."""

from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.account.auth.api.dependencies.services import get_user_service
from app.account.auth.helpers.enums import AuthMessages
from app.account.auth.models import User
from app.account.auth.repository.services import UserService
from app.account.auth.schemas import UserInput, UserRegisterOutput
from toolkit.api.enums import HTTPStatusDoc, OpenAPITags, Status

router = APIRouter(prefix="/users", tags=[OpenAPITags.USERS])


@router.post(
    "/register", status_code=status.HTTP_201_CREATED, response_model=UserRegisterOutput
)
async def register(
    user_input: UserInput,
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
    user_input : UserInput
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
