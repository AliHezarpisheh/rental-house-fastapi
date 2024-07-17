"""Module for defining base configurations."""

from .database.base import AsyncDatabaseConnection
from .logging.base import LoggingConfig

# Database
db = AsyncDatabaseConnection()

# Logging
logger = LoggingConfig().get_logger()
