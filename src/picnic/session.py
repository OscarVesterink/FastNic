"""Set up the Picnic connection."""
import logging

import python_picnic_api

from src.core import config

settings = config.get_settings()
PICNIC_USERNAME = settings.PICNIC_USERNAME
PICNIC_PASSWORD = settings.PICNIC_PASSWORD

logger = logging.getLogger(settings.LOGGER_CONTROLLERS_NAME)


def get_picnic_client() -> python_picnic_api.PicnicAPI:
    """Get the Picnic client.

    Returns:
        The Picnic client.

    #TODO: Add a retry mechanism.
    #TODO: Add a generator.

    """
    return python_picnic_api.PicnicAPI(
        username=PICNIC_USERNAME, password=PICNIC_PASSWORD, country_code="NL"
    )
