"""Module containing custom exception handlers for FastAPI applications."""

import logging

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from toolkit.api.enums import HTTPStatusDoc, Status
from toolkit.api.exceptions import (
    BaseTokenError,
    CustomHTTPException,
    DoesNotExistError,
)

logger = logging.getLogger(__name__)


async def custom_http_exception_handler(
    request: Request, exc: CustomHTTPException
) -> JSONResponse:
    """
    Handle CustomHTTPException raised within FastAPI routes.

    Parameters
    ----------
    request : Request
        The incoming request object.
    exc : CustomHTTPException
        The instance of CustomHTTPException raised.

    Returns
    -------
    JSONResponse
        JSON response containing error details, including status code,
        error message, details, and documentation link if available.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "status": str(exc.status),
                "message": exc.message,
                "details": exc.details,
                "documentation_link": exc.documentation_link,
            }
        },
    )


async def request_validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> None:
    """
    Handle RequestValidationError by raising a CustomHTTPException with details.

    This function is an exception handler specifically designed to handle
    RequestValidationError exceptions raised within FastAPI routes.
    It raises a CustomHTTPException with a status code of 422 (Unprocessable Entity)
    and includes details such as the error message, reason, affected field,
    and a documentation link.

    Parameters
    ----------
    request : Request
        The incoming request object.
    exc : RequestValidationError
        The instance of RequestValidationError raised.

    Raises
    ------
    CustomHTTPException
        Always raises a CustomHTTPException with a status code of 422
        (Unprocessable Entity).
    """
    exc_data = exc.errors()[0]
    logger.error("Request validation error occurred. Error details: %s", exc_data)
    raise CustomHTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        status=Status.VALIDATION_ERROR,
        message=exc_data["msg"],
        field=f"{exc_data['loc'][1]}, in: {exc_data['loc'][0]}",
        reason=exc_data["type"],
        documentation_link=HTTPStatusDoc.STATUS_422,
    )


async def does_not_exist_exception_handler(
    request: Request, exc: DoesNotExistError
) -> None:
    """
    Handle DoesNotExistError by raising a CustomHTTPException with details.

    This function is an exception handler specifically designed to handle
    DoesNotExistError exceptions and its children raised within FastAPI routes.
    It raises a CustomHTTPException with a status code of 404 (Not Found)
    and includes details such as the error message, reason, affected field,
    and a documentation link.

    Parameters
    ----------
    request : Request
        The incoming request object.
    exc : DoesNotExistError
        The instance of DoesNotExistError raised.

    Raises
    ------
    CustomHTTPException
        Always raises a CustomHTTPException with a status code of 404 (Not Found).
    """
    logger.error("Does not exist error occurred. Error details: %s", exc)
    raise CustomHTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        status=Status.NOT_FOUND,
        message=str(exc),
        documentation_link=HTTPStatusDoc.STATUS_404,
    )


async def base_token_error_handler(request: Request, exc: BaseTokenError) -> None:
    """
    Handle BaseTokenError by raising a CustomHTTPException with details.

    This function is an exception handler specifically designed to handle
    BaseTokenError exceptions raised within FastAPI routes.
    It raises a CustomHTTPException with a status code of 401 (Unauthorized)
    and includes details such as the error message, reason, affected field,
    and a documentation link.

    Parameters
    ----------
    request : Request
        The incoming request object.
    exc : BaseTokenError
        The instance of BaseTokenError raised.

    Raises
    ------
    CustomHTTPException
        Always raises a CustomHTTPException with a status code of 401 (Unauthorized).
    """
    logger.error("Base token error occurred. Error details: %s", exc)
    raise CustomHTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        status=Status.FORBIDDEN,
        message=str(exc),
        documentation_link=HTTPStatusDoc.STATUS_403,
    )
