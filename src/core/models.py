import logging
from datetime import datetime, timezone

import sqlalchemy
from sqlalchemy import orm

from src.core import config
from src.database import session as database_session

settings = config.get_settings()
logger = logging.getLogger(settings.LOGGER_CONTROLLERS_NAME)


class GlobalModel(database_session.Base):
    """Global model inherited by all other models.

    Attributes:
        created_at: The time the model was created.
        updated_at: The time the model was last updated.

    """

    __abstract__ = True

    created_at = sqlalchemy.Column(
        sqlalchemy.DateTime(),
        default=datetime.now(tz=timezone.utc),
        nullable=False,
    )
    updated_at = sqlalchemy.Column(
        sqlalchemy.DateTime(),
        default=datetime.now(tz=timezone.utc),
        onupdate=datetime.now(tz=timezone.utc),
        nullable=False,
    )
