"""Custom exceptions related to API interactions."""


class TokenError(Exception):
    """Base class for token-related exceptions."""


class DoesNotExistError(Exception):
    """Exception raised when a requested resource does not exist."""


class DuplicateResourceError(Exception):
    """Exception raised when a resource already exists."""
