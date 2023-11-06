""" Business logic for the health router. """
import logging

import python_picnic_api

from src.core.config import get_settings

logger = logging.getLogger(get_settings().LOGGER_CONTROLLERS_NAME)


def check_picnic_connection(
    pc_session: python_picnic_api.PicnicAPI,
) -> bool:
    """Check the connection to ElasticSearch.

    Returns:
        True if the connection is successful, False otherwise.
    """
    logger.info("Pinging Picnic API.")
    return pc_session.logged_in()
