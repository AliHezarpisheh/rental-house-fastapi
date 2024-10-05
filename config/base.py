"""Module for defining base configurations."""

from .database.base import AsyncDatabaseConnection
from .logging import LoggingConfig
from .settings import settings

# Database
db = AsyncDatabaseConnection()

# Logging
logger = LoggingConfig().get_logger(settings.env)
