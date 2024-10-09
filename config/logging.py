"""Module for configuring logging settings."""

import logging
import logging.config
import logging.handlers
import os
from pathlib import Path
from typing import Any

import coloredlogs

from toolkit.parsers import TOMLParser


class RelativePathFilter:
    """A logging filter that adds a `relativepath` attribute to log records."""

    def filter(self, record: logging.LogRecord) -> bool:
        """
        Modify the log record to include a `relativepath` attribute.

        Parameters
        ----------
        record : logging.LogRecord
            The log record that is being processed by the filter.

        Returns
        -------
        bool
            Returns True to indicate that the log record should be processed.

        Notes
        -----
        The `relativepath` is computed based on the `record.pathname` using
        the current working directory as the starting point.
        """
        record.relativepath = os.path.relpath(record.pathname, start=os.getcwd())
        return True


class LoggingConfig:
    """Class for configuring logging settings based on a specified config file."""

    def __init__(
        self, environment: str = "development", config_path: str = "settings.toml"
    ) -> None:
        self._env = environment
        self._parser = TOMLParser(file_path=config_path)
        self._logger: logging.Logger | None = None

    def get_logger(self) -> logging.Logger:
        """Return a logger instance, initializing it if necessary."""
        if self._logger is None:
            self.setup()
        assert self._logger is not None, "Logger setup failed to initialize logger"
        return self._logger

    def setup(self) -> None:
        """Set up the logging configurations."""
        logging_config = self._parser.read()["logging"]

        # Check or create the dirs of log files specified in the config.
        handlers = logging_config.get("handlers", None)
        self.validate_and_create_dirs(handlers=handlers)

        # Determine the appropriate logger configuration based on the environment.
        logger_config = logging_config["loggers"].get(self._env)

        if logger_config:
            logging_config["loggers"][""] = logger_config

        logging.config.dictConfig(logging_config)

        # Set the logger object.
        self._logger = logging.getLogger()

        # Add relativepath filter to all the handlers
        for handler in self._logger.handlers:
            handler.addFilter(RelativePathFilter())

        # Set up coloredlogs
        coloredlogs.install(
            level="DEBUG",
            logger=self._logger,
            fmt=logging_config["formatters"]["coreFormatter"]["format"],
            datefmt=logging_config["formatters"]["coreFormatter"]["datefmt"],
        )

    @staticmethod
    def validate_and_create_dirs(handlers: dict[str, dict[str, Any]]) -> list[Path]:
        """
        Validate the configuration and create directories specified in handlers.

        Parameters
        ----------
        handlers : dict
            Dictionary containing logging handlers.

        Notes
        -----
        The function checks for the existence of directories specified
        in the 'filename' attribute of each handler in the configuration.
        If the directories do not exist, they are created.
        """
        paths = []
        for handler in handlers.values():
            handler_path = handler.get("filename", None)
            if handler_path is not None:
                path = Path(handler_path)
                if not path.exists():
                    path.parent.mkdir(parents=True, exist_ok=True)
                    paths.append(path)
        return paths
