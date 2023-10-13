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

    ingredients: orm.Mapped["Ingredient"] = orm.relationship(
        back_populates="recipe", cascade="save-update"
    )


class Ingredient(GlobalModel):
    """Definition of the Ingredient model.

    Attributes:
        id: The unique identifier of the ingredient.
        name: The name of the ingredient.
        recipe_id: The id of the parent recipe of the ingredient.

    Relationships:
        recipe: The recipe the ingredient belongs to (one-to-many).

    """

    __tablename__ = "ingredients"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    name = sqlalchemy.Column(sqlalchemy.String(128), nullable=False)
    recipe_id = sqlalchemy.Column(
        sqlalchemy.Integer,
        sqlalchemy.ForeignKey("recipes.id"),
        nullable=True,
    )

    recipe: orm.Mapped["Recipe"] = orm.relationship(
        back_populates="ingredients", cascade="save-update"
    )
