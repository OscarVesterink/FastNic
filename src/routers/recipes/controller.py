""" Business logic for the recipes router. """
import logging

from sqlalchemy import orm

from src.core import models, schemas
from src.core.config import get_settings
from src.database import crud as database_crud

logger = logging.getLogger(get_settings().LOGGER_CONTROLLERS_NAME)


def get_all_investigations(db_session: orm.Session) -> list[schemas.RecipeOutputSchema]:
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


def get_investigation_by_id(
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
) -> models.Recipe:
    """Creates a recipe.

    Args:
        recipe: The recipe to create.
        db_session: The database session.
        pc_session: The picnic session.

    Returns:
        The created recipe.

    """
    logger.info(f"Creating recipe {recipe.name}.")
    new_recipe = database_crud.create(models.Recipe(**recipe.dict()), db_session)

    logger.info(f"Saving recipe {recipe.name}.")
    db_session.commit()

    return new_recipe


def patch_investigation(
    recipe_update: schemas.RecipeUpdateSchema,
    recipe_id: int,
    db_session: orm.Session,
) -> schemas.RecipeOutputSchema:
    """Updates a recipe.

    Args:
        recipe_update: The recipe details to update.
        recipe_id: The id of the recipe to update.
        db_session: The database session.

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
