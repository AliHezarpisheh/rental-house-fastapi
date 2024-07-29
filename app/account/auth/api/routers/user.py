"""Module defines routers related to users."""

from fastapi import APIRouter, status

from app.account.auth.schemas.user import UserInput
from toolkit.api.enums import OpenAPITags

router = APIRouter(prefix="/users", tags=[OpenAPITags.USERS])


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    user_input: UserInput,
) -> None:
    """Register a new user."""  # TODO: Complete the docstring using markdown.
