"""Module defines exceptions related to auth and users."""

from toolkit.api.exceptions import DuplicateResourceError


class DuplicateUserError(DuplicateResourceError):
    """Exception raised when a user already exists."""
