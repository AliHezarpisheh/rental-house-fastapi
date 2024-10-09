"""Module for defining base configurations."""

from .database import AsyncDatabaseConnection
from .logging import LoggingConfig
from .settings.base import get_settings

# Settings
settings = get_settings()

# Database
db = AsyncDatabaseConnection(database_url=settings.database_url)

# Logging
logger = LoggingConfig(environment=settings.env).get_logger()
