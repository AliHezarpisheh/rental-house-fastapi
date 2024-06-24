"""Module for defining base configurations."""

from .database.base import DatabaseConnection
from .logging.base import LoggingConfig
from .settings import settings

# Database
db = DatabaseConnection()

# Logging
log = LoggingConfig()
logger = log.get_logger(settings.env)
