""" Contains endpoints for interacting with the orders table."""

import fastapi
from fastapi import status
from sqlalchemy import orm
import python_picnic_api

from src.core import openapi, schemas
from src.database import session as database_session
from src.picnic import session as picnic_session
from src.routers.orders import controller


router = fastapi.APIRouter(
    prefix="/orders",
)


@router.post(
    "",
    summary="Create an order.",
    description="This endpoint requires a payload with the details of an "
    "order; it creates a order in Picnic.",
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "The created order."},
    },
    response_model=list[schemas.IngredientOutputSchema],
    tags=["Orders"],
)
def post_order(
    order: schemas.OrderInputSchema = fastapi.Body(
        ..., description=openapi.Descriptions.order_payload
    ),
    db_session: orm.Session = fastapi.Depends(database_session.get_database),
    pc_session: python_picnic_api.PicnicAPI = fastapi.Depends(
        picnic_session.get_picnic_client
    ),
) -> list[schemas.IngredientOutputSchema]:
    """Creates an order for Picnic.

    Attributes:
        order: The order to create.
        db_session: The database session.
        pc_session: The Picnic API session.

    Returns:
        The list of ingredients in the order.

    """
    return controller.post_order(
        order=order, db_session=db_session, pc_session=pc_session
    )
