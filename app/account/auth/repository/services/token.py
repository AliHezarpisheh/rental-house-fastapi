"""
Module for token service operations.

This module provides a service class for handling various token-related operations.
"""

from dataclasses import asdict
from datetime import datetime, timedelta, timezone

import jwt

from app.account.auth.helpers.exceptions import InternalTokenError
from app.account.auth.models import User
from app.account.auth.schemas.token import JwtClaims
from config.base import logger, settings
from toolkit.api.enums.messages import Messages


class TokenService:
    """Service class for token-related operations."""

    TOKEN_TYPE = "Bearer"

    def grant_token(self, user: User) -> dict[str, str]:
        """
        Generate and return a JWT access token for the specified user.

        Parameters
        ----------
        user : User
            The user for whom the token is being generated.

        Returns
        -------
        dict[str, str]
            A dictionary containing the access token and token type.

        Raises
        ------
        TokenError
            If an internal error occurs during token encoding.
        """
        assert settings.jwt_private_key is not None, "JWT private key is not set."
        payload = self._generate_payload(user=user)
        try:
            token = jwt.encode(
                payload=asdict(payload),
                key=settings.jwt_private_key,
                algorithm=settings.jwt_algorithm,
            )
        except TypeError as err:
            logger.error("Couldn't encode the jwt.", exc_info=True)
            raise InternalTokenError(Messages.INTERNAL_SERVER_ERROR) from err

        return {"access_token": token, "type": self.TOKEN_TYPE}

    def _generate_payload(self, user: User) -> JwtClaims:
        """
        Generate the payload for a JWT token.

        Parameters
        ----------
        user : User
            The user for whom the token payload is being generated.

        Returns
        -------
        JwtClaims
            A dataclass instance representing the JWT claims.
        """
        current_datetime = self._get_current_datetime()
        expiration_datetime = self._add_timedelta(
            dtm=current_datetime, minutes=settings.jwt_lifetime_minutes
        )
        return JwtClaims(
            sub=user.id,
            aud=["all"],
            iat=current_datetime,
            nbf=current_datetime,
            exp=expiration_datetime,
        )

    @staticmethod
    def _get_current_datetime() -> datetime:
        """
        Get the current datetime in UTC.

        Returns
        -------
        datetime
            The current datetime in UTC.
        """
        return datetime.now(timezone.utc)

    @staticmethod
    def _add_timedelta(dtm: datetime, minutes: int) -> datetime:
        """
        Add a timedelta to a given datetime object.

        Parameters
        ----------
        dtm : datetime
            The datetime object to which the timedelta will be added.
        minutes : int
            The number of minutes to add.

        Returns
        -------
        datetime
            A new datetime object with the added timedelta.
        """
        return dtm + timedelta(minutes=minutes)
