import logging
from datetime import datetime, timezone

import sqlalchemy
from sqlalchemy import orm

from src.core import config
from src.database import session as database_session

settings = config.get_settings()
logger = logging.getLogger(settings.LOGGER_CONTROLLERS_NAME)


class GlobalModel(database_session.Base):
    """Global model inherited by all other models.

    Attributes:
        created_at: The time the model was created.
        updated_at: The time the model was last updated.

    """

    __abstract__ = True

    created_at = sqlalchemy.Column(
        sqlalchemy.DateTime(),
        default=datetime.now(tz=timezone.utc),
        nullable=False,
    )
    updated_at = sqlalchemy.Column(
        sqlalchemy.DateTime(),
        default=datetime.now(tz=timezone.utc),
        onupdate=datetime.now(tz=timezone.utc),
        nullable=False,
    )


class Recipe(GlobalModel):
    """Definition of the Recipe model.

    Attributes:
        id: The unique identifier of the recipe.
        name: The name of the recipe.
        category: The category of the recipe.

    Relationships:
        ingredients: The ingredients of the recipe (one-to-many).

    """

    __tablename__ = "recipes"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String(128), nullable=False)
    category = sqlalchemy.Column(sqlalchemy.String(128), nullable=False)

    ingredients: orm.Mapped[list["Ingredient"]] = orm.relationship(
        back_populates="recipe", cascade="save-update"
    )


class Product(GlobalModel):
    """Definition of the Product model.

    Attributes:
        id: The unique identifier of the product.
        name: The name of the product.
        image_uri: The uri of the image of the product.

    Relationships:
        ingredient: The ingredient the product belongs to (one-to-many).

    """

    __tablename__ = "products"

    id = sqlalchemy.Column(sqlalchemy.String(50), primary_key=True)
    name = sqlalchemy.Column(sqlalchemy.String(255), nullable=False)
    image_uri = sqlalchemy.Column(sqlalchemy.String(255), nullable=True)

    ingredients: orm.Mapped[list["Ingredient"]] = orm.relationship(
        back_populates="product", cascade="all, delete"
    )


class Ingredient(GlobalModel):
    """Definition of the Ingredient model.

    Attributes:
        id: The unique identifier of the ingredient.
        name: The name of the ingredient.
        quantity: The quantity of the ingredient in the recipe, default=1.
        recipe_id: The id of the parent recipe of the ingredient.
        product_id: The id of the parent product of the ingredient.

    Relationships:
        recipe: The recipe the ingredient belongs to (one-to-many).
        product: The product the ingredient belongs to (one-to-many).

    """

    __tablename__ = "ingredients"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String(128), nullable=False)
    quantity = sqlalchemy.Column(sqlalchemy.Integer, nullable=False, default=1)
    recipe_id = sqlalchemy.Column(
        sqlalchemy.Integer,
        sqlalchemy.ForeignKey("recipes.id"),
        nullable=True,
    )
    product_id = sqlalchemy.Column(
        sqlalchemy.Integer,
        sqlalchemy.ForeignKey("products.id"),
        nullable=True,
    )

    recipe: orm.Mapped["Recipe"] = orm.relationship(
        back_populates="ingredients", cascade="save-update"
    )
    product: orm.Mapped["Product"] = orm.relationship(
        back_populates="ingredients", cascade="save-update"
    )
