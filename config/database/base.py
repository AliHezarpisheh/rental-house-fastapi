"""Module for defining base database configurations."""

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, scoped_session, sessionmaker

from config.settings import settings


class DatabaseConnection:
    """Class for managing database connections."""

    def __init__(self) -> None:
        """Initialize DatabaseConnection with the specified configuration path."""
        self._engine: Engine | None = None

    def get_engine(self) -> Engine:
        """
        Get the database engine.

        Returns
        -------
        sqlalchemy.engine.Engine
            The database engine object.
        """
        if not self._engine:
            self._engine = create_engine(settings.database_url)
        return self._engine

    def get_session(self) -> scoped_session[Session]:
        """
        Get a scoped database session.

        Returns
        -------
        sqlalchemy.orm.scoped_session[Session]
            A scoped session object.
        """
        engine = self.get_engine()
        Session = sessionmaker(bind=engine)
        return scoped_session(Session)
