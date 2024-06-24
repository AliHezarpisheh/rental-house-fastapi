"""Custom exceptions related to API interactions."""


class BaseTokenError(Exception):
    """Base class for token-related exceptions."""


class InvalidTokenError(BaseTokenError):
    """Exception raised when the provided token is invalid."""


class DoesNotExistError(Exception):
    """Exception raised when a requested resource does not exist."""
