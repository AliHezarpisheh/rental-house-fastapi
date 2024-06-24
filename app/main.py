"""
Module serves the FastAPI instance for the backend application.

It initializes the FastAPI application, configures middleware, setting lifespan context
manager, and defines routes for handling various HTTP requests.
"""

from fastapi import FastAPI

from config.settings import settings
from config.settings.openapi import responses

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


# Add health-check endpoint
@app.get("/health")
def get_health() -> str:
    """Router for health-check of the application."""
    return {"status": "OK"}
