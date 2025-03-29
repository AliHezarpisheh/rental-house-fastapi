"""Module defines schemas for users."""

from __future__ import annotations

from typing import Annotated

from pydantic import EmailStr, Field

from toolkit.api.schemas.base import APIResponse, BaseSchema
from toolkit.api.schemas.mixins import CommonMixins


class UserRegisterInputSchema(BaseSchema):
    """Input schema for creating a new user."""

    email: EmailStr
    password: str


class UserAuthenticateInputSchema(BaseSchema):
    """Input schema for user login."""

    email: EmailStr
    password: str


class UserOutputDataSchema(CommonMixins, BaseSchema):
    """User output data schema."""

    email: Annotated[str, Field(description="")]
    is_active: Annotated[bool, Field(description="")]
    is_verified: Annotated[bool, Field(description="")]


class UserOutputSchema(APIResponse):
    """Output schema for successful user operations output, containing the user data."""

    data: UserOutputDataSchema
