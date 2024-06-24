"""Module defining Pydantic models for error handling in API responses."""

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from ..enums import HTTPStatusDoc, Status


class ErrorDetails(BaseModel):
    """Details of an error including reason and responsible field."""

    reason: str = Field(..., description="The reason for the error.")
    field: str = Field(
        ..., description="The field responsible for the error, if applicable."
    )


class APIError(BaseModel):
    """Structure of an API error response."""

    status: Status = Field(..., description="The status of the error.")
    message: str = Field(
        ..., description="A human-readable message describing the error."
    )
    details: Optional[ErrorDetails] = Field(
        None, description="Additional details about the error."
    )
    documentation_link: Optional[HTTPStatusDoc] = Field(
        None,
        description=(
            "A link to documentation providing further information on the error."
        ),
    )

    # model configuration
    model_config = ConfigDict(use_enum_values=True)


class BaseError(BaseModel):
    """Wrapper for an APIError providing information about the error."""

    error: APIError = Field(..., description="Information about the error.")


class BadRequest(BaseError):
    """Represents a 400 Bad Request error."""

    error: APIError = Field(
        ...,
        description="Information about the 400 Bad Request error.",
        examples=[
            {
                "status": "400",
                "message": "Bad request. Invalid or missing parameters.",
                "details": {
                    "field": "parameter_name",
                    "reason": (
                        "Description of the reason why the parameter is invalid or "
                        "missing."
                    ),
                },
                "documentation_link": (
                    "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/400"
                ),
            },
        ],
    )


class Unauthorized(BaseError):
    """Represents a 401 Unauthorized error."""

    error: APIError = Field(
        ...,
        description="Information about the 401 Unauthorized error.",
        examples=[
            {
                "status": "401",
                "message": "Unauthorized. User is not authenticated.",
                "documentation_link": (
                    "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/401"
                ),
            },
        ],
    )


class Forbidden(BaseError):
    """Represents a 403 Forbidden error."""

    error: APIError = Field(
        ...,
        description="Information about the 403 Forbidden error.",
        examples=[
            {
                "status": "403",
                "message": "User does not have permission to access this resource.",
                "documentation_link": (
                    "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/403"
                ),
            },
        ],
    )


class NotFound(BaseError):
    """Represents a 404 Not Found error."""

    error: APIError = Field(
        ...,
        description="Information about the 404 Not Found error.",
        examples=[
            {
                "status": "404",
                "message": "Not Found. The requested resource does not exist.",
                "documentation_link": (
                    "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/404"
                ),
            },
        ],
    )


class Conflict(BaseError):
    """Represents a 409 Conflict error."""

    error: APIError = Field(
        ...,
        description="Information about the 409 Conflict error.",
        examples=[
            {
                "status": "409",
                "message": (
                    "Conflict. The request conflicts with the current state of the "
                    "server."
                ),
                "documentation_link": (
                    "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/409"
                ),
            },
        ],
    )


class UnprocessableEntity(BaseError):
    """Represents a 422 Unprocessable Entity error."""

    error: APIError = Field(
        ...,
        description="Information about the 422 Unprocessable Entity error.",
        examples=[
            {
                "status": "422",
                "message": (
                    "Unprocessable Entity. The request is well-formed but unable to be "
                    "processed due to semantic errors."
                ),
                "details": {
                    "field": "entity_name",
                    "reason": "Description of the semantic error.",
                },
                "documentation_link": (
                    "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/422"
                ),
            },
        ],
    )


class InternalServerError(BaseError):
    """Represents a 500 Internal Server Error."""

    error: APIError = Field(
        ...,
        description="Information about the 500 Internal Server Error.",
        examples=[
            {
                "status": "500",
                "message": (
                    "Internal Server Error. An unexpected condition was encountered on "
                    "the server."
                ),
                "documentation_link": (
                    "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/500",
                ),
            },
        ],
    )
