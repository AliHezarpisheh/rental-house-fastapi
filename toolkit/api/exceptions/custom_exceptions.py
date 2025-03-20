"""Custom exceptions related to server and external services like db."""

import fastapi

from toolkit.api.enums import HTTPStatusDoc, Status

from .abc import APIException


class BadRequestError(APIException):
    """Exception raised when a bad request happened."""

    status_code = fastapi.status.HTTP_400_BAD_REQUEST
    status = Status.ERROR
    documentation_link = HTTPStatusDoc.HTTP_STATUS_400


class ValidationError(APIException):
    """Exception raised when a validation error happened."""

    status_code = fastapi.status.HTTP_422_UNPROCESSABLE_ENTITY
    status = Status.ERROR
    documentation_link = HTTPStatusDoc.HTTP_STATUS_422


class InternalServerError(APIException):
    """Exception raised when an internal error happened."""

    status_code = fastapi.status.HTTP_500_INTERNAL_SERVER_ERROR
    status = Status.FAILURE
    documentation_link = HTTPStatusDoc.HTTP_STATUS_500


class ServiceUnavailableError(APIException):
    """Exception raised when a service is not available."""

    status_code = fastapi.status.HTTP_503_SERVICE_UNAVAILABLE
    status = Status.FAILURE
    documentation_link = HTTPStatusDoc.HTTP_STATUS_503
