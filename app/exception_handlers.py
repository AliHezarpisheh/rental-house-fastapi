"""Module containing custom exception handlers for FastAPI applications."""

import fastapi
from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import ORJSONResponse

from config.base import logger
from toolkit.api.enums import HTTPStatusDoc, Messages, Status
from toolkit.api.exceptions import APIException


async def internal_exception_handler(
    request: Request, exc: Exception
) -> ORJSONResponse:
    """
    Handle unexpected internal server errors.

    This handler catches unhandled exceptions in FastAPI routes and returns a
    standardized JSON response with a 500 status code.

    Parameters
    ----------
    request : Request
        The incoming request object.
    exc : Exception
        The unhandled exception raised during request processing.

    Returns
    -------
    ORJSONResponse
        A response object containing the error details.
    """
    logger.critical("Unhandled error occurred. Exception details: %s", exc)
    return ORJSONResponse(
        status_code=fastapi.status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status": Status.ERROR.value,
            "message": Messages.INTERNAL_SERVER_ERROR.value,
            "documentation_link": HTTPStatusDoc.HTTP_STATUS_500.value,
        },
    )


async def request_validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> ORJSONResponse:
    """
    Handle FastAPI's RequestValidationError.

    This handler captures validation errors raised by FastAPI/Pydantic during request
    parsing and returns a structured response with a 422 status code.

    Parameters
    ----------
    request : Request
        The incoming request object.
    exc : RequestValidationError
        The validation exception raised during request parsing.

    Returns
    -------
    ORJSONResponse
        A response object containing the validation error details.
    """
    exc_data = exc.errors()[0]
    message = exc.errors()[0]["msg"]
    reason = exc.errors()[0]["type"]
    loc = exc_data["loc"][0]
    field = exc_data["loc"][1] if len(exc_data["loc"]) >= 2 else "-" + f", in: {loc}"
    logger.error(
        "Handle request pydantic validation exception. Exception details: %s", exc_data
    )
    return ORJSONResponse(
        status_code=fastapi.status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "status": Status.VALIDATION_ERROR.value,
            "message": message,
            "details": {"field": field, "reason": reason},
            "documentation_link": HTTPStatusDoc.HTTP_STATUS_422.value,
        },
    )


async def api_exception_error_handler(
    request: Request, exc: APIException
) -> ORJSONResponse:
    """
    Handle all the API exceptions in the code.

    This handler is the place where python `APIException` subclasses transform to a
    HTTP response.

    Parameters
    ----------
    request : Request
        The incoming request object.
    exc : APIException
        The APIException (or subclass) raised.

    Returns
    -------
    ORJSONResponse
        A response object containing the error details.
    """
    logger.error("Handle %s. Exception details: %s", exc.__class__.__name__, exc)
    return ORJSONResponse(
        status_code=exc.status_code,
        content=exc.to_jsonable_dict(),
        headers=exc.http_headers,
    )
