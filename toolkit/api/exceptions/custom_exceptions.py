"""Custom exceptions related to API interactions."""


class UnauthorizedError(Exception):
    """Base class raised when an unauthenticated access occurred."""


class ForbiddenError(Exception):
    """Base class for token-related exceptions."""


class DoesNotExistError(Exception):
    """Exception raised when a requested resource does not exist."""


class DuplicateResourceError(Exception):
    """Exception raised when a resource already exists."""
