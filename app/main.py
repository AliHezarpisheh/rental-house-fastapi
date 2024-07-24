"""
Module serves the FastAPI instance for the backend application.

It initializes the FastAPI application, configures middleware, setting lifespan context
manager, and defines routes for handling various HTTP requests.
"""

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

from config.settings import settings
from config.settings.openapi import responses
from toolkit.api.exceptions import (
    BaseTokenError,
    CustomHTTPException,
    DoesNotExistError,
)

from .exception_handlers import (
    base_token_error_handler,
    custom_http_exception_handler,
    does_not_exist_exception_handler,
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
    BaseTokenError,
    base_token_error_handler,  # type: ignore
)

# Include routers
app.include_router(health_check_router)
