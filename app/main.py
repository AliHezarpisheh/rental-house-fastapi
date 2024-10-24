"""
Module serves the FastAPI instance for the backend application.

It initializes the FastAPI application, configures middleware, setting lifespan context
manager, and defines routes for handling various HTTP requests.
"""

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import ORJSONResponse

from app.account.auth.api.routers.user import router as users_router
from app.account.otp.api.routers.otp import router as otp_router
from config.base import settings
from config.settings.openapi import responses
from toolkit.api.exceptions import (
    CustomHTTPException,
    DoesNotExistError,
    DuplicateResourceError,
    TokenError,
)

from .exception_handlers import (
    custom_http_exception_handler,
    does_not_exist_exception_handler,
    duplicate_resource_error_handler,
    request_validation_exception_handler,
    token_error_handler,
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
    CustomHTTPException,
    custom_http_exception_handler,  # type: ignore
)
app.add_exception_handler(
    RequestValidationError,
    request_validation_exception_handler,  # type: ignore
)
app.add_exception_handler(
    DoesNotExistError,
    does_not_exist_exception_handler,  # type: ignore
)
app.add_exception_handler(
    TokenError,
    token_error_handler,  # type: ignore
)
app.add_exception_handler(
    DuplicateResourceError,
    duplicate_resource_error_handler,  # type: ignore
)

# Include routers
app.include_router(health_check_router)
app.include_router(users_router)
app.include_router(otp_router)
