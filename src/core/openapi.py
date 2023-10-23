"""Centralizes the OpenAPI definitions for the API."""
import enum


class Descriptions(str, enum.Enum):
    """A class to hold the descriptions of OpenAPI variables. This has been centralized
    to ensure that the descriptions are consistent across the API.
    """

    dummy = "This is a dummy description."


def get_openapi_tags_metadata() -> list[dict[str, str]]:
    """Returns the tag definitions for the swagger documentation.

    Returns:
        The tag definitions.

    """
    return [
        {
            "name": "Header",
            "description": "A small description related to the header.",
        },
        {
            "name": "Health",
            "description": "Operations to check the health of the API.",
        },
    ]
