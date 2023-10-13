"""Contains the configurations of the API."""
import functools
from typing import Union

import pydantic


class Settings(pydantic.BaseSettings):
    """Sets up the environment variables."""

    APP_NAME: str = "FastNic"
    LOGGING_REQUESTS_FILE: str = pydantic.Field(
        "requests_logging.txt", env="LOGGING_REQUESTS_FILE"
    )
    LOGGER_REQUESTS_NAME: str = pydantic.Field(
        "Backend Requests Logger", env="LOGGER_REQUESTS_NAME"
    )
    LOGGING_CONTROLLERS_FILE: str = pydantic.Field(
        "controller_logging.txt", env="LOGGING_CONTROLLER_FILE"
    )
    LOGGER_CONTROLLERS_NAME: str = pydantic.Field(
        "Backend Controller Logger", env="LOGGER_CONTROLLER_NAME"
    )
    ROOT_PATH: str = pydantic.Field("/api/v1", env="ROOT_PATH")

    SQLALCHEMY_DATABASE_TYPE: str = pydantic.Field("sqlite", env="DATABASE_TYPE")
    SQL_USER: str = pydantic.Field("INSECURE_USER", env="SQL_USER")
    SQL_PASSWORD: str = pydantic.Field("INSECURE_PASSWORD", env="SQL_PASSWORD")
    SQL_HOST: str = pydantic.Field("127.0.0.1", env="SQL_HOST")
    SQL_PORT: str = pydantic.Field("5432", env="SQL_PORT")
    SQL_DATABASE: str = pydantic.Field("fastnic", env="SQL_DATABASE")

    PICNIC_USERNAME: str = pydantic.Field("INSECURE_USERNAME", env="PICNIC_USERNAME")
    PICNIC_PASSWORD: str = pydantic.Field("INSECURE_PASSWORD", env="PICNIC_PASSWORD")

    SERVICE_CONNECTION_TIMEOUT: int = pydantic.Field(
        300, env="SERVICE_TIMEOUT"
    )  # in seconds
    SERVICE_CONNECTION_RETRY_DELAY: int = pydantic.Field(
        5, env="SERVICE_RETRY_DELAY"
    )  # in seconds

    @pydantic.validator(
        "S3_SECURE_CONNECTION",
    )
    def convert_environment_variable_to_boolean(cls, value: Union[str, bool]) -> bool:
        """Converts the environment variable to a boolean.

        Args:
            value: The environment variable.

        Returns:
            The boolean.

        Raises:
            ValueError: If the environment variable is cannot be converted to a boolean.

        """
        if isinstance(value, bool):
            return value

        true_set = {"true", "1", "t", "yes", "y", "on"}
        false_set = {"false", "0", "f", "no", "n", "off"}
        if value.lower() in true_set | false_set:
            return value.lower() in true_set

        raise ValueError(
            f"The environment variable with value {value} cannot be converted to a "
            "boolean."
        )


@functools.lru_cache()
def get_settings() -> Settings:
    """Cached call to the environment variables.

    Returns:
        Settings: An object containing the environment variables.

    """
    return Settings()
