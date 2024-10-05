"""Module defines routers related to users."""

from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.account.auth.api.dependencies.services import get_user_service
from app.account.auth.repository.services import UserService
from app.account.auth.schemas import UserInput
from toolkit.api.enums import OpenAPITags

router = APIRouter(prefix="/users", tags=[OpenAPITags.USERS])


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    user_input: UserInput,
    user_service: Annotated[UserService, Depends(get_user_service)],
):
    """Register a new user."""  # TODO: Complete the docstring using markdown.
    user = await user_service.register(user_input=user_input)
    return user
