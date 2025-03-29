"""Module defines schemas for tokens."""

import uuid
from datetime import datetime
from typing import Literal

import pydantic
from pydantic import Field

from toolkit.api.schemas import BaseSchema


@pydantic.dataclasses.dataclass
class JwtClaims:
    """Pydantic dataclass representing JWT claims."""

    sub: int
    aud: list[str] | str
    iat: datetime
    nbf: datetime
    exp: datetime
    jti: str = Field(default_factory=lambda: str(uuid.uuid4()))
    issue: str = "rental_house_fastapi"


class TokenOutputSchema(BaseSchema):
    """Output schema for granting user an access token with the token type."""

    access_token: str
    type: Literal["Bearer"] = "Bearer"
