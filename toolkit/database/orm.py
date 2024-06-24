"""Module provides ORM functionality for database interaction."""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for declarative ORM models."""
