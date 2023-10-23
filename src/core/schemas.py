"""Schemas for input and output at the endpoints."""
import logging
import datetime
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


class BaseOutputModel(pydantic.BaseModel):
    """Base output model inherited by all other output models.

    Attributes:
        id: The unique identifier of the model.
        created_at: The time the model was created.
        updated_at: The time the model was last updated.

    """

    id: str = pydantic.Field(
        ...,
        title="ID",
        description="The internal primary key of the model.",
    )
    created_at: datetime.datetime = pydantic.Field(
        ...,
        title="Created At",
        description="The time the source file was created.",
    )
    updated_at: datetime.datetime = pydantic.Field(
        ...,
        title="Updated At",
        description="The time the source file was last updated.",
    )


class RecipeInputSchema(pydantic.BaseModel):
    name: str = pydantic.Field(
        ...,
        title="Name",
        description="The name of the recipe.",
    )
    category: str = pydantic.Field(
        ...,
        title="Category",
        description="The category of the recipe.",
    )


class ProductInputSchema(pydantic.BaseModel):
    id: str = pydantic.Field(
        ...,
        title="ID",
        description="The ID of the product.",
    )
    name: str = pydantic.Field(
        ...,
        title="Name",
        description="The name of the product.",
    )
    category: str = pydantic.Field(
        ...,
        title="Category",
        description="The category of the product.",
    )
    image_uri: str = pydantic.Field(
        ...,
        title="Image URI",
        description="The URI of the image of the product.",
    )


class IngredientInputSchema(pydantic.BaseModel):
    name: str = pydantic.Field(
        ...,
        title="Name",
        description="The name of the ingredient.",
    )
    quantity: float = pydantic.Field(
        ...,
        title="Quantity",
        description="The quantity of the ingredient.",
    )


class RecipeUpdateSchema(RecipeInputSchema):
    __annotations__ = make_all_fields_optional(RecipeInputSchema)


class ProductUpdateSchema(ProductInputSchema):
    __annotations__ = make_all_fields_optional(ProductInputSchema)


class IngredientUpdateSchema(IngredientInputSchema):
    __annotations__ = make_all_fields_optional(IngredientInputSchema)


class IngredientOutputSchema(BaseOutputModel, IngredientInputSchema):
    recipe_id: str = pydantic.Field(
        ...,
        title="Recipe ID",
        description="The ID of the parent recipe of the ingredient.",
    )
    product_id: str = pydantic.Field(
        ...,
        title="Product ID",
        description="The ID of the parent product of the ingredient.",
    )


class RecipeOutputSchema(BaseOutputModel, RecipeInputSchema):
    ingredients: list[IngredientOutputSchema] = pydantic.Field(
        ...,
        title="Ingredients",
        description="The ingredients of the recipe.",
    )


class ProductOutputSchema(BaseOutputModel, ProductInputSchema):
    ingredients: list[IngredientOutputSchema] = pydantic.Field(
        ...,
        title="Ingredients",
        description="The ingredients of the product.",
    )
