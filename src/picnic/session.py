"""Set up the Picnic connection."""
import logging
from typing import Iterator

import python_picnic_api

from src.core.config import get_settings

logger = logging.getLogger(get_settings().LOGGER_CONTROLLERS_NAME)


def get_picnic_client() -> Iterator[python_picnic_api.PicnicAPI]:
    """Get the Picnic client.

    Returns:
        The Picnic client.

    #TODO: Add a retry mechanism.

    """
    try:
        client = python_picnic_api.PicnicAPI(
            username=get_settings().PICNIC_USERNAME,
            password=get_settings().PICNIC_PASSWORD,
            country_code="NL",
        )
    except Exception as e:
        logger.error("Error while connecting to Picnic API: %s", e)
        raise

    try:
        logger.debug("Opening Picnic API connection")
        yield client
    except Exception as e:
        logger.error("Error while using Picnic API: %s", e)
        raise
