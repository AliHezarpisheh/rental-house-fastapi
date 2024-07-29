"""Module defines schemas for users."""

from __future__ import annotations

from pydantic import EmailStr

from toolkit.api.schemas.base import BaseSchema


class UserInput(BaseSchema):
    """Input schema for creating a new user."""

    username: str
    email: EmailStr
    password: str
