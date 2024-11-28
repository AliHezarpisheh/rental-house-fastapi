"""
Module for token service operations.

This module provides a service class for handling various token-related operations.
"""

from app.account.auth.models import User


class TokenService:
    """Service class for token-related operations."""

    def grant_token(self, user: User) -> dict[str, str]:
        """Fix this."""
        return {"access_token": "test"}

    def verify_token(self, token: str) -> None:
        """Fix this."""
        pass

    def _serialize_jwt_claims(self, payload: dict[str, str]) -> None:
        """Fix this."""
        pass
