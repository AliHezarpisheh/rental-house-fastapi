"""Module for handling all the settings in the application."""

import os
from typing import Annotated, Type

from pydantic import Field
from pydantic_settings import (
    BaseSettings,
    DotEnvSettingsSource,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    TomlConfigSettingsSource,
)

from .enums import Env
from .openapi import OpenAPISettings


class Settings(BaseSettings):
    """
    Class for handling all the settings in the application.

    Notes
    -----
    The `model_config` attribute is a `SettingsConfigDict` instance. It contains the
    following attributes:
        - toml_file: str
            The file path to the TOML settings file.
        - env_file: str
            The file path to the environments variable settings file.
    """

    # TOML Settings
    openapi: OpenAPISettings

    # .env Settings
    env: Env

    # PostgreSQL settings
    database_url: Annotated[str, Field(..., description="Database connection URL.")]

    # Redis settings
    redis_host: Annotated[
        str, Field(..., description="Redis server's hostname/IP.")
    ] = "localhost"
    redis_port: Annotated[
        int, Field(..., description="The port the Redis instance is running.")
    ] = 6037
    redis_db: Annotated[
        int, Field(..., description="Redis database (Accepted values: 0-15)")
    ] = 0
    redis_password: Annotated[str, Field(..., description="Redis instance password.")]
    redis_pool_max_connection: Annotated[
        int, Field(..., description="Redis pool max connection limit.")
    ] = 100

    # OTP settings
    otp_ttl: Annotated[int, Field(..., description="OTPs time-to-live.")] = 300
    otp_digits: Annotated[int, Field(..., description="OTP digits number.")] = 6

    # API settings
    origins: Annotated[
        list[str], Field(..., description="List of allowed API origins.")
    ]

    # Settings config
    model_config = SettingsConfigDict(
        toml_file="settings.toml",
        env_file=f".env.{os.getenv('ENV', 'development')}",
        case_sensitive=False,
        use_enum_values=True,
        extra="ignore",
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: Type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        """Customise the settings sources."""
        return (
            init_settings,  # Initial settings
            TomlConfigSettingsSource(settings_cls),  # Read from .toml file
            DotEnvSettingsSource(settings_cls),  # Read from .env file
            env_settings,  # Read from environments variables
            file_secret_settings,  # Read from any file secret settings if applicable
        )
