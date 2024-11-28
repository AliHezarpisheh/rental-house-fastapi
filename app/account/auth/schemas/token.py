"""Module defines schemas for tokens."""

from typing import Literal

import pydantic
from pydantic.types import UUID4

from toolkit.api.schemas import BaseSchema


@pydantic.dataclasses.dataclass
class JwtClaims:
    """Pydantic dataclass representing JWT claims."""

    issue: str
    sub: str
    aud: str
    iat: int
    nbf: int
    exp: int
    jti: UUID4


class TokenOutput(BaseSchema):
    """Output schema for granting user an access token with the token type."""

    access_token: str
    type: Literal["Bearer"] = "Bearer"
