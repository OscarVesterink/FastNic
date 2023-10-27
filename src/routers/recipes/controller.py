""" Business logic for the recipes router. """
import logging

from sqlalchemy import orm
import python_picnic_api

from src.core import models, schemas
from src.core.config import get_settings
from src.database import crud as database_crud

logger = logging.getLogger(get_settings().LOGGER_CONTROLLERS_NAME)


def _get_ingredients_from_picnic(
    pc_session: python_picnic_api.PicnicAPI,
) -> list[dict[str, str]]:
    """Gets the ingredients from picnic.

    Args:
        pc_session: The picnic session.

    Returns:
        The ingredients.
    """
    logger.debug(f"Getting recipe ingredients from picnic.")
    ingredients_list = pc_session.get_cart()["items"]
    return [ingredient["items"][0] for ingredient in ingredients_list]


def _add_ingredients_to_recipe(
    db_session: orm.Session,
    recipe: models.Recipe,
    ingredients: list[dict[str, str]],
) -> None:
    """Adds ingredients to a recipe.

    Args:
        db_session: The database session.
        recipe: The recipe to add ingredients to.
        ingredients: The ingredients to add.

    Returns:
        None

    """
    for ingredient in ingredients:
        product = _get_product_from_db(db_session=db_session, ingredient=ingredient)
        new_ingredient = models.Ingredient(
            name=ingredient["name"],
            quantity=ingredient["decorators"][0]["quantity"],
            product=product,
            recipe=recipe,
        )
        db_session.add(new_ingredient)


def _get_product_from_db(
    db_session: orm.Session,
    ingredient: dict[str, str],
) -> models.Product:
    """Gets a product from the database or creates it if it doesn't exist.

    Args:
        db_session: The database session.
        ingredient: The ingredient to get the product for.

    Returns:
        The product.

    """
    logger.debug(f"Getting product {ingredient['name']} from database or create it.")
    product = database_crud.read_or_create(
        models.Product(
            id=ingredient["id"],
            name=ingredient["name"],
            image_uri=ingredient["image_ids"][0],
        ),
        db_session,
        [
            models.Product.id == ingredient["id"],
        ],
    )

    return product


def get_all_recipes(db_session: orm.Session) -> list[schemas.RecipeOutputSchema]:
    """Returns a list of all recipes.

    Args:
        db_session: The database session.

    Returns:
        A list of all recipes.

    """
    logger.info("Getting all recipes")
    return database_crud.read(
        models.Recipe,
        db_session,
        [],
    )


def get_recipe_by_id(
    recipe_id: int, db_session: orm.Session
) -> schemas.RecipeOutputSchema:
    """Returns a recipe selected with its id.

    Args:
        recipe_id: The identifier of the recipe.
        db_session: The database session.

    Returns:
        The recipe selected.

    """
    logger.info(f"Getting recipe {recipe_id}.")
    return database_crud.read(
        models.Recipe,
        db_session,
        [
            models.Recipe.id == recipe_id,
        ],
        expected_count=1,
    )[0]


def post_recipe(
    recipe: schemas.RecipeInputSchema,
    db_session: orm.Session,
    pc_session: python_picnic_api.PicnicAPI,
) -> schemas.RecipeOutputSchema:
    """Creates a recipe.

    Args:
        recipe: The recipe to create.
        db_session: The database session.
        pc_session: The picnic session.

    Returns:
        The created recipe.

    """
    logger.debug(f"Creating recipe {recipe.name}.")
    new_recipe = database_crud.create(
        models.Recipe(
            name=recipe.name,
            category=recipe.category,
        ),
        db_session,
    )

    ingredients_list = _get_ingredients_from_picnic(pc_session=pc_session)

    logger.debug(f"Adding ingredients to recipe {recipe.name}.")
    _add_ingredients_to_recipe(
        db_session=db_session,
        recipe=new_recipe,
        ingredients=ingredients_list,
    )

    logger.info(f"Saving recipe {recipe.name}.")
    db_session.commit()

    return new_recipe


def patch_recipe(
    recipe_update: schemas.RecipeUpdateSchema,
    recipe_id: int,
    db_session: orm.Session,
    pc_session: python_picnic_api.PicnicAPI,
) -> schemas.RecipeOutputSchema:
    """Updates a recipe.

    Args:
        recipe_update: The recipe details to update.
        recipe_id: The id of the recipe to update.
        db_session: The database session.
        pc_session: The picnic session.

    Returns:
        The updated recipe.

    """
    logger.info(f"Updating recipe {recipe_id}.")
    recipe = database_crud.update(
        recipe_update.dict(exclude_unset=True),
        models.Recipe,
        db_session,
        [models.Recipe.id == recipe_id],
    )

    ingredients_list = _get_ingredients_from_picnic(pc_session=pc_session)

    logger.debug(f"Adding ingredients to recipe {recipe.name}.")
    _add_ingredients_to_recipe(
        db_session=db_session,
        recipe=recipe,
        ingredients=ingredients_list,
    )

    logger.info(f"Saving recipe {recipe.name}.")
    db_session.commit()
    return recipe


def delete_recipe(
    recipe_id: int,
    db_session: orm.Session,
) -> None:
    """Deletes a recipe and all it's children.

    Args:
        recipe_id: The id of the recipe to delete.
        db_session: The database session.

    Returns:
        None

    """
    logger.info(f"Deleting recipe {recipe_id} and its ingredients from database.")
    database_crud.delete(
        models.Recipe,
        db_session,
        [models.Recipe.id == recipe_id],
    )

    db_session.commit()
