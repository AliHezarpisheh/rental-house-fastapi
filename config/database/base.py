"""Module for defining base database configurations."""

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from config.settings import settings


class AsyncDatabaseConnection:
    """Class for managing async database connections."""

    def __init__(self) -> None:
        """Initialize AsyncDatabaseConnection with the specified configuration path."""
        self._engine: AsyncEngine | None = None

    def get_engine(self) -> AsyncEngine:
        """
        Get the async database engine.

        Returns
        -------
        sqlalchemy.ext.asyncio.AsyncEngine
            The async database engine object.
        """
        if not self._engine:
            self._engine = create_async_engine(settings.database_url)
        return self._engine

    def get_session(self) -> scoped_session:
        """
        Get a scoped async database session.

        Returns
        -------
        sqlalchemy.orm.scoped_session
            A scoped async session object.
        """
        engine = self.get_engine()
        async_session = sessionmaker(
            bind=engine, class_=AsyncSession, expire_on_commit=False
        )
        return scoped_session(async_session)
