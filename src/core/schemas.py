from __future__ import annotations

import logging
from typing import Optional, Type

import pydantic

from src.core import config

settings = config.get_settings()
logger = logging.getLogger(settings.LOGGER_CONTROLLERS_NAME)


def make_all_fields_optional(schema: Type[pydantic.BaseModel]) -> dict:
    """Makes all fields of a schema optional.

    Args:
        schema: The schema to make all fields optional.

    Returns:
        A schema with all fields optional.

    """
    return {k: Optional[v] for k, v in schema.__annotations__.items()}
