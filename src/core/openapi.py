"""Centralizes the OpenAPI definitions for the API."""
import enum


class Descriptions(str, enum.Enum):
    """A class to hold the descriptions of OpenAPI variables. This has been centralized
    to ensure that the descriptions are consistent across the API.
    """

    dummy = "This is a dummy description."

    recipe_id = "The identifier of the recipe."

    recipe_payload = "The payload of the recipe."
    order_payload = "The payload of the order."
    promo_payload = "The payload of the promo."


def get_openapi_tags_metadata() -> list[dict[str, str]]:
    """Returns the tag definitions for the swagger documentation.

    Returns:
        The tag definitions.

    """
    return [
        {
            "name": "Health",
            "description": "Operations to check the health of the API.",
        },
        {
            "name": "Recipes",
            "description": "CRUD operations to manage recipes.",
        },
        {
            "name": "Orders",
            "description": "CRUD operations to manage orders.",
        },
        {
            "name": "Dealicious",
            "description": "CRUD operations to manage discounts.",
        },
    ]
