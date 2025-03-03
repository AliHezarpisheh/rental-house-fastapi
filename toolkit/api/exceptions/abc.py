"""Module holding abstract base classes for the application."""

from abc import ABC, abstractmethod

from toolkit.api.enums import HTTPStatusDoc, Status


class APIException(ABC, Exception):
    """Base exception for all API-related errors, handled in exception handlers."""

    def __init__(
        self,
        message: str,
        http_headers: dict[str, str] | None = None,
        field: str | None = None,
        reason: str | None = None,
    ) -> None:
        """
        Initialize an `APIException` object.

        Both of the `field` and `reason` should be set, or both should be leaved unset.
        If one of them is set and the other is unset, an `AssertionError` will be
        raised.
        """
        assert not (
            bool(field) ^ bool(reason)
        ), "`field` and `reason` should be both set or unset"

        self.message = message
        self.field = field
        self.reason = reason
        self.http_headers = http_headers
        super().__init__(message)

    @property
    @abstractmethod
    def status_code(self) -> int:
        """HTTP status code associated with the exception."""

    @property
    @abstractmethod
    def status(self) -> Status:
        """Short status message for the exception."""

    @property
    @abstractmethod
    def documentation_link(self) -> HTTPStatusDoc:
        """URL to relevant documentation."""

    def to_jsonable_dict(self) -> dict[str, str]:
        """Return error data as a jsonable dictionary."""
        error_data = {
            "status": self.status.value,
            "message": self.message,
            "documentationLink": self.documentation_link.value,
        }
        if self.field and self.reason:
            error_data.update({"field": self.field, "reason": self.reason})
        return error_data
