"""Module containing token and JWT related data structures and services."""

import pydantic
from pydantic.types import UUID4


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


class TokenService:
    """Service class for token-related operations."""
