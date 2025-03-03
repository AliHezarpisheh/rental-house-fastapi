"""
Module serves the FastAPI instance for the backend application.

It initializes the FastAPI application, configures middleware, setting lifespan context
manager, and defines routes for handling various HTTP requests.
"""

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import ORJSONResponse

from app.account.otp.api.routers.totp import router as totp_router
from config.base import settings
from config.settings.openapi import responses
from toolkit.api.exceptions import APIException

from .exception_handlers import (
    api_exception_error_handler,
    internal_exception_handler,
    request_validation_exception_handler,
)
from .healthcheck import router as health_check_router
from .lifespan import lifespan

# Setup FastAPI instance
app = FastAPI(
    title=settings.openapi.title,
    version=settings.openapi.version,
    description=settings.openapi.description,
    contact=settings.openapi.contact.model_dump(),
    license_info=settings.openapi.license.model_dump(),
    openapi_tags=[tag.model_dump() for tag in settings.openapi.tags],
    responses=responses,
    default_response_class=ORJSONResponse,
    redoc_url=None,
    lifespan=lifespan,
)

# Register custom exception handlers
app.add_exception_handler(
    Exception,
    internal_exception_handler,
)
app.add_exception_handler(
    RequestValidationError,
    request_validation_exception_handler,  # type: ignore
)
app.add_exception_handler(
    APIException,
    api_exception_error_handler,  # type: ignore
)

# Include routers
app.include_router(health_check_router)
app.include_router(totp_router)
