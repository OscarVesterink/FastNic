"""Contains the configurations of the API."""
import functools
import dotenv

import pydantic
import pydantic_settings

dotenv.load_dotenv()


class Settings(pydantic_settings.BaseSettings):
    """Sets up the environment variables."""

    APP_NAME: str = "FastNic"
    LOGGING_REQUESTS_FILE: str = pydantic.Field(
        "requests_logging.txt", alias="LOGGING_REQUESTS_FILE"
    )
    LOGGER_REQUESTS_NAME: str = pydantic.Field(
        "Backend Requests Logger", alias="LOGGER_REQUESTS_NAME"
    )
    LOGGING_CONTROLLERS_FILE: str = pydantic.Field(
        "controller_logging.txt", alias="LOGGING_CONTROLLER_FILE"
    )
    LOGGER_CONTROLLERS_NAME: str = pydantic.Field(
        "Backend Controller Logger", alias="LOGGER_CONTROLLER_NAME"
    )
    ROOT_PATH: str = pydantic.Field("/api/v1", alias="ROOT_PATH")

    SQLALCHEMY_DATABASE_TYPE: str = pydantic.Field("sqlite", alias="DATABASE_TYPE")
    SQL_USER: str = pydantic.Field("INSECURE_USER", alias="SQL_USER")
    SQL_PASSWORD: str = pydantic.Field("INSECURE_PASSWORD", alias="SQL_PASSWORD")
    SQL_HOST: str = pydantic.Field("127.0.0.1", alias="SQL_HOST")
    SQL_PORT: str = pydantic.Field("5432", alias="SQL_PORT")
    SQL_DATABASE: str = pydantic.Field("fastnic", alias="SQL_DATABASE")

    PICNIC_USERNAME: str = pydantic.Field("INSECURE_USERNAME", alias="PICNIC_USERNAME")
    PICNIC_PASSWORD: str = pydantic.Field("INSECURE_PASSWORD", alias="PICNIC_PASSWORD")

    SERVICE_CONNECTION_TIMEOUT: int = pydantic.Field(
        300, unit="s", alias="SERVICE_TIMEOUT"
    )
    SERVICE_CONNECTION_RETRY_DELAY: int = pydantic.Field(
        5, unit="s", alias="SERVICE_RETRY_DELAY"
    )


@functools.lru_cache()
def get_settings() -> Settings:
    """Cached call to the environment variables.

    Returns:
        Settings: An object containing the environment variables.

    """
    return Settings()
