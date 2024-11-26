"""Module defines exceptions related to auth and users."""

from toolkit.api.exceptions import DoesNotExistError, DuplicateResourceError


class UserDoesNotExistError(DoesNotExistError):
    """Exception raised when a user is not found."""


class DuplicateUserError(DuplicateResourceError):
    """Exception raised when a user already exists."""
