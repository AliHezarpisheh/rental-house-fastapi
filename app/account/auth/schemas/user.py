"""Module defines schemas for users."""

from __future__ import annotations

from typing import Annotated

from pydantic import EmailStr, Field

from toolkit.api.schemas.base import APIResponse, BaseSchema
from toolkit.api.schemas.mixins import CommonMixins


class UserInput(BaseSchema):
    """Input schema for creating a new user."""

    username: str
    email: EmailStr
    password: str


class UserOutputData(CommonMixins, BaseSchema):
    """User output data schema."""

    username: Annotated[str, Field(description="")]
    email: Annotated[str, Field(description="")]
    is_active: Annotated[bool, Field(description="")]
    is_verified: Annotated[bool, Field(description="")]


class UserRegisterOutput(APIResponse):
    """Output schema for successful user register."""

    data: UserOutputData
