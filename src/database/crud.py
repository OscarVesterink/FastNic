"""CRUD operations."""
from __future__ import annotations

import logging
import time
from typing import Any, Callable, Iterable, Type, Union

import fastapi
from fastapi import status
from sqlalchemy import exc, orm
from sqlalchemy.sql import elements, operators

from src.core import config, models
from src.database import session as database_session

settings = config.get_settings()
logger = logging.getLogger(settings.LOGGER_CONTROLLERS_NAME)
SERVICE_CONNECTION_TIMEOUT = settings.SERVICE_CONNECTION_TIMEOUT
SERVICE_CONNECTION_RETRY_DELAY = settings.SERVICE_CONNECTION_RETRY_DELAY


def _retry_sql_alchemy_error(
    function: Callable,
) -> Callable:
    """Decorator to retry a function if it raises a SQLAlchemy error.

    Args:
        function: The function to retry.

    Returns:
        The return value of the function.

    Notes:
        There seems to be an occasional SQLAlchemy error when calling the
        database after a long period of inactivity on police infrastructure.
        This decorator will retry the function if it raises an SQLAlchemy error.
    """

    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return function(*args, **kwargs)
        except exc.SQLAlchemyError as error:
            logger.error(f"SQLAlchemy error: {error}")
            time.sleep(0.5)
            return function(*args, **kwargs)

    return wrapper


def read_or_create(
    new_model: models.GlobalModel,
    session: orm.Session,
    query: Iterable[elements.BinaryExpression],
) -> models.GlobalModel:
    """Get a model if it exists, otherwise create it.

    Args:
        new_model: The model to create if it doesn't exist.
        session: The database session.
        query: The arguments to filter by.

    Returns:
        Instance of the created/queried model.

    """
    logger.info(
        f"Getting the {new_model.__class__.__name__} if it exists, otherwise creating it."
    )
    query_results = read(new_model.__class__, session, query)
    if len(query_results) > 1:
        logger.error("Found multiple matching rows; query is not specific enough.")
        raise ValueError("Found multiple matching rows; query is not specific enough.")
    elif len(query_results) == 1:
        return query_results[0]
    else:
        return create(new_model, session)


@_retry_sql_alchemy_error
def read(
    model: type[models.GlobalModel],
    session: orm.Session,
    query: Iterable[
        Union[Type[elements.BinaryExpression], Type[operators.ColumnOperators]]
    ],
    expected_count: int | None = None,
) -> list[models.GlobalModel]:
    """Get a model if it exists.

    Args:
        model: The model class.
        session: The database session.
        query: The arguments to filter by.
        expected_count: The expected number of results. If None, any number of results
                        is allowed.

    Returns:
        List of instances of the queried model.

    Raises:
        404: If too few models are found.
        406: If too many models are found.
        500: If the connection to the database fails.

    """
    logger.info(f"Querying for {model.__name__}")
    results = session.query(model).filter(*query).all()  # type: ignore

    if expected_count is None or len(results) == expected_count:
        return results

    logger.error(f"Expected {expected_count} {model.__name__} but found {len(results)}")
    if len(results) < expected_count:
        raise fastapi.HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not enough models match the query.",
        )
    else:
        raise fastapi.HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="Too many models match the query.",
        )


@_retry_sql_alchemy_error
def create(new_model: models.GlobalModel, session: orm.Session) -> models.GlobalModel:
    """Create a model.

    Args:
        new_model: The model to create.
        session: The database session.

    Returns:
        Instance of the created model.

    Raises:
        500 If the connection to the database fails.

    """
    logger.info(f"Creating {new_model.__class__.__name__}")
    session.add(new_model)
    session.flush()
    session.refresh(new_model)

    return new_model


def update(
    params: dict,
    model: type[models.GlobalModel],
    session: orm.Session,
    query: Iterable[elements.BinaryExpression],
) -> models.GlobalModel:
    """Update a model.

    Args:
        params: The parameters to update. Keys correspond to column names and values are
                the new values.
        model: The model class.
        session: The database session.
        query: The arguments to filter by.

    Returns:
        The updated model.

    Raises:
        400: If the provided parameters are invalid.

    """
    target_model = read(model, session, query, expected_count=1)[0]

    if any([not hasattr(target_model, key) for key in params]):
        logging.error("one or more parameters are not valid to update model.")
        raise fastapi.HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="One or more parameters are not valid.",
        )

    logger.info(f"Updating {target_model.__class__.__name__} with {params}")
    for key, value in params.items():
        setattr(target_model, key, value)
    return target_model


@_retry_sql_alchemy_error
def delete(
    model: type[models.GlobalModel],
    session: orm.Session,
    query: Iterable[elements.BinaryExpression],
) -> str:
    """Delete a model.

    Args:
        model: The model class.
        session: The database session.
        query: The arguments to filter by.

    Returns:
        "ok" if the model was deleted.

    Raises:
        HTTPException: 500 If the connection to the database fails.

    """
    logging.info(f"Deleting model:{model.__name__} ")
    target_model = read(model, session, query, expected_count=1)[0]
    session.delete(target_model)

    return "ok"


def create_metadata() -> None:
    """Create the database metadata. Includes a timeout and retry delay to allow the
    database to start up after the API.

    """
    start_time = time.time()

    while time.time() - start_time < SERVICE_CONNECTION_TIMEOUT:
        try:
            logger.info("Creating metadata table")
            database_session.Base.metadata.create_all(bind=database_session.engine)
            return None
        except exc.OperationalError as exception_info:
            if "psycopg2.OperationalError" in exception_info.args[0]:
                logger.info(
                    f"Could not connect to database. Retrying in {SERVICE_CONNECTION_RETRY_DELAY} seconds..."
                )
                time.sleep(SERVICE_CONNECTION_RETRY_DELAY)
            else:
                raise exception_info

    logger.error("Could not connect to SQL database.")
    raise fastapi.HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Could not connect to SQL database.",
    )
