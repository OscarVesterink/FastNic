""" Business logic for the recipes router. """
import logging

from sqlalchemy import orm
import python_picnic_api

from src.core import models, schemas
from src.core.config import get_settings
from src.database import crud as database_crud

logger = logging.getLogger(get_settings().LOGGER_CONTROLLERS_NAME)


def post_order(
    order: schemas.OrderInputSchema,
    db_session: orm.Session,
    pc_session: python_picnic_api.PicnicAPI,
) -> list[schemas.IngredientOutputSchema]:
    """Creates an order.

    Args:
        order: The order to create.
        db_session: The database session.
        pc_session: The picnic session.

    Returns:
        The list of ingredients in the order.

    """
    logger.debug("Creating order.")
    shopping_cart = []
    for recipe_name in order.recipes:
        recipe = database_crud.read(
            models.Recipe,
            db_session,
            [
                models.Recipe.name == recipe_name,
            ],
            expected_count=1,
        )[0]
        logger.debug(f"Adding recipe {recipe.name} to order.")
        for ingredient in recipe.ingredients:
            shopping_cart.append(ingredient)
            pc_session.add_product(ingredient.product.id, count=ingredient.quantity)

    logger.info("Order created.")
    return shopping_cart
