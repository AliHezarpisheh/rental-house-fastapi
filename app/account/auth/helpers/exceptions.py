"""Module defines exceptions related to auth and users."""

from toolkit.api.exceptions import (
    DoesNotExistError,
    DuplicateResourceError,
    UnauthorizedError,
)


class UserDoesNotExistError(DoesNotExistError):
    """Exception raised when a user is not found."""


class DuplicateUserError(DuplicateResourceError):
    """Exception raised when a user already exists."""


class InvalidUserCredentials(UnauthorizedError):
    """Exception raised when the user is not authenticated."""
