"""Module holding enumerations related to the project's settings."""

from enum import StrEnum


class EnvEnum(StrEnum):
    """Enumeration class define different environments."""

    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"
