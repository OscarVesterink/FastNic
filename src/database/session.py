"""Set up the database connection."""
import logging
import os
from typing import Generator

import sqlalchemy
from sqlalchemy import engine, orm

from src.core import config

settings = config.get_settings()
SQLALCHEMY_DATABASE_TYPE = settings.SQLALCHEMY_DATABASE_TYPE
SQL_USER = settings.SQL_USER
SQL_PASSWORD = settings.SQL_PASSWORD
SQL_HOST = settings.SQL_HOST
SQL_PORT = settings.SQL_PORT
SQL_DATABASE = settings.SQL_DATABASE
logger = logging.getLogger(settings.LOGGER_CONTROLLERS_NAME)


def get_engine(database_type: str) -> engine.Engine:
    """Get the database engine.

    Args:
        database_type: The type of database to use. Can be either "sqlite" or
            "mysql".

    Returns:
        The database engine.

    Raises:
        ValueError: If the database type is invalid.

    Notes:
        Standard fastAPI code will have the engine as a global variable. This
        was modified to be a function so the engine can be modified during
        integration tests.
    """

    if database_type == "sqlite":
        logger.info("Using SQLite database.")
        url = os.getenv("SQLITE_DATABASE", "sqlite:///test.db")
        local_engine = sqlalchemy.create_engine(
            url, future=True, echo=False, connect_args={"check_same_thread": False}
        )
    elif database_type == "postgresql":
        logger.info("Using PostgreSQL database.")
        url = (
            f"postgresql://{SQL_USER}:"
            + f"{SQL_PASSWORD}@{SQL_HOST}:"
            + f"{SQL_PORT}/{SQL_DATABASE}"
        )
        local_engine = sqlalchemy.create_engine(url, future=True)
    else:
        logger.error("Invalid database type.")
        raise ValueError("Invalid database type.")
    return local_engine


engine = get_engine(SQLALCHEMY_DATABASE_TYPE)  # type: ignore
SessionLocal = orm.sessionmaker(  # type: ignore
    autocommit=False, autoflush=False, bind=engine, future=True
)
Base = orm.declarative_base()


def get_database() -> Generator[orm.Session, None, None]:
    """Get a database session. Session is closed upon exiting the generator.

    Returns:
        Generator containing the database session.

    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
