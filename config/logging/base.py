"""Module for configuring logging settings."""

import logging
import logging.config
import logging.handlers
from pathlib import Path
from typing import Any

from toolkit.parsers import TOMLParser


class LoggingConfig:
    """Class for configuring logging settings based on a specified config file."""

    def __init__(self, config_path: str = "logging.toml") -> None:
        self._parser = TOMLParser(file_path=config_path)

    def get_logger(self, name: str) -> logging.Logger:
        """Get a logger with the specified name."""
        return logging.getLogger(name)

    def setup(self) -> None:
        """Set up the logging configurations."""
        logging_config = self._parser.read()
        # Check or Create the dirs of log files specified in the config.
        handlers = logging_config.get("handlers", None)
        self.validate_and_create_dirs(handlers=handlers)
        logging.config.dictConfig(logging_config)

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
