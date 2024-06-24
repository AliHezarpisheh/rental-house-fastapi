"""Define custom HTTPExceptions for fastapi applications."""

from typing import Optional

from fastapi import HTTPException


class CustomHTTPException(HTTPException):
    """
    Custom exception class for representing HTTP errors in fastapi applications.

    Attributes
    ----------
    status_code : int
        The status of the error. This is different from HTTP status_code (e.g., error).
    status : str
        A human-readable description of the HTTP status (e.g., "Service Unavailable").
    message : str
        A concise description of the error message.
    field : str, optional
        The name of the parameter or field associated with the error (default is None).
    reason : str, optional
        A detailed explanation of why the parameter or field is invalid
        (default is None).
    documentation_link : str
        The URL link to the documentation explaining the HTTP status code.
    headers : dict[str, str] or None, optional
        Additional headers to include in the error response (default is None).
    """

    def __init__(
        self,
        *,
        status_code: int,
        status: str,
        message: str,
        field: Optional[str] = None,
        reason: Optional[str] = None,
        documentation_link: str,
        headers: dict[str, str] | None = None,
    ) -> None:
        """Initialize a CustomHTTPException instance."""
        self.status = status
        self.message = message
        self.documentation_link = documentation_link
        self.details = None

        if (reason is not None) and (field is not None):
            self.details = {
                "field": field,
                "reason": reason,
            }
        super().__init__(status_code, headers)
