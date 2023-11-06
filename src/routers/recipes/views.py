""" Contains endpoints for interacting with the recipes table."""

import fastapi
from fastapi import status
from sqlalchemy import orm
import python_picnic_api

from src.core import openapi, schemas
from src.database import session as database_session
from src.picnic import session as picnic_session
from src.routers.recipes import controller


router = fastapi.APIRouter(
    prefix="/recipes",
)


@router.get(
    "",
    summary="Get a list of all recipes.",
    description="This endpoint requires no input; it returns a list of all recipes.",
    responses={200: {"description": "A list of all recipes"}},
    response_model=list[schemas.RecipeOutputSchema],
    tags=["Recipes"],
)
def get_all_recipes(
    db_session: orm.Session = fastapi.Depends(database_session.get_database),
) -> list[schemas.RecipeOutputSchema]:
    """Get a list of all recipes.

    Args:
        db_session: The database session.

    Returns:
        A list of all recipes.

    """
    return controller.get_all_recipes(db_session=db_session)


@router.get(
    "/{recipe_id}",
    summary="Get a recipe by its ID.",
    description="This endpoint requires a recipe ID; it returns the "
    "recipe with that ID.",
    responses={
        200: {"description": "The recipe with the given ID."},
        404: {"description": "Recipe not found."},
    },
    response_model=schemas.RecipeOutputSchema,
    tags=["Recipes"],
)
def get_recipe_by_id(
    recipe_id: int = fastapi.Path(
        ..., gt=0, description=openapi.Descriptions.recipe_id
    ),
    db_session: orm.Session = fastapi.Depends(database_session.get_database),
) -> schemas.RecipeOutputSchema:
    """Get a recipe by its ID.

    Args:
        recipe_id: The ID of the recipe.
        db_session: The database session.

    Returns:
        The recipe with the given ID.

    """
    return controller.get_recipe_by_id(recipe_id=recipe_id, db_session=db_session)


@router.post(
    "",
    summary="Create a recipe.",
    description="This endpoint requires a payload with the details of a "
    "recipe; it creates a recipe.",
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "The created recipe."},
    },
    response_model=schemas.RecipeOutputSchema,
    tags=["Recipes"],
)
def post_recipe(
    recipe: schemas.RecipeInputSchema = fastapi.Body(
        ..., description=openapi.Descriptions.recipe_payload
    ),
    db_session: orm.Session = fastapi.Depends(database_session.get_database),
    pc_session: python_picnic_api.PicnicAPI = fastapi.Depends(
        picnic_session.get_picnic_client
    ),
) -> schemas.RecipeOutputSchema:
    """Creates a recipe.

    Attributes:
        recipe: The recipe to create.
        db_session: The database session.
        pc_session: The Picnic API session.

    Returns:
        The created recipe.

    """
    return controller.post_recipe(
        recipe=recipe, db_session=db_session, pc_session=pc_session
    )


@router.patch(
    "/{recipe_id}",
    summary="Update a recipe.",
    description="This endpoint requires a payload with the details of a "
    "recipe; it updates a recipe. When the shopping cart contains ingredients,"
    "the recipe will be updated with the ingredients from the shopping cart.",
    responses={
        200: {"description": "The updated recipe."},
        404: {"description": "The recipe does not exist."},
    },
    response_model=schemas.RecipeOutputSchema,
    tags=["Recipes"],
)
def patch_recipe(
    recipe_update: schemas.RecipeUpdateSchema,
    recipe_id: int = fastapi.Path(
        ..., gt=0, description=openapi.Descriptions.recipe_id
    ),
    db_session: orm.Session = fastapi.Depends(database_session.get_database),
    pc_session: python_picnic_api.PicnicAPI = fastapi.Depends(
        picnic_session.get_picnic_client
    ),
) -> schemas.RecipeOutputSchema:
    """Updates a recipe.

    Attributes:
        recipe_update: The updated recipe data.
        recipe_id: The identifier of the recipe to update.
        db_session: The database session.
        pc_session: The Picnic API session.

    Returns:
        The updated recipe.

    """
    return controller.patch_recipe(
        recipe_update=recipe_update,
        recipe_id=recipe_id,
        db_session=db_session,
        pc_session=pc_session,
    )


@router.delete(
    "/{recipe_id}",
    summary="Delete a recipe.",
    description="This endpoint requires the id of a recipe; it deletes the recipe.",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        204: {"description": "The recipe was deleted."},
        404: {"description": "The recipe does not exist."},
    },
    tags=["Recipes"],
)
def delete_recipe(
    recipe_id: int = fastapi.Path(
        ..., gt=0, description=openapi.Descriptions.recipe_id
    ),
    db_session: orm.Session = fastapi.Depends(database_session.get_database),
) -> None:
    """Delete a recipe.

    Args:
        recipe_id: The id of the recipe.
        db_session: The database session.
    """
    return controller.delete_recipe(recipe_id=recipe_id, db_session=db_session)
