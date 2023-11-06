""" Contains endpoints for interacting with the dealicious controller."""

import fastapi
from fastapi import status
import python_picnic_api

from src.core import openapi
from src.picnic import session as picnic_session
from src.routers.dealicious import controller


router = fastapi.APIRouter(
    prefix="/dealicious",
)


@router.post(
    "/combine",
    summary="It will look into the shopping cart to combine discounts.",
    description="This endpoint requires no payload; it will look into the shopping cart to combine discounts.",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        204: {"description": "Discounts combined."},
        400: {"description": "Unavailable products in cart."},
    },
    tags=["Dealicious"],
)
def post_combine(
    pc_session: python_picnic_api.PicnicAPI = fastapi.Depends(
        picnic_session.get_picnic_client
    ),
) -> None:
    """Looks into the shopping cart to combine discounts.

    Attributes:
        pc_session: The Picnic API session.

    Returns:
        204: Discounts combined.

    """
    return controller.post_combine(pc_session=pc_session)


@router.get(
    "/promo",
    summary="It will look into the shopping cart to search for all promo discount.",
    description="This endpoint requires no payload; it will look into the shopping cart for all promo discounts.",
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Promo found."},
        400: {"description": "Unavailable products in cart."},
    },
    response_model=list[dict],
    tags=["Dealicious"],
)
def get_promo(
    pc_session: python_picnic_api.PicnicAPI = fastapi.Depends(
        picnic_session.get_picnic_client
    ),
) -> list[dict]:
    """Looks into the shopping cart for promo discounts.

    Attributes:
        pc_session: The Picnic API session.

    Returns:
        A list with possibile promo discounts.

    """
    return controller.get_promo(pc_session=pc_session)


@router.post(
    "/promo",
    summary="It will look into the shopping cart to apply all promo discount.",
    description="This endpoint requires no payload; it will look into the shopping cart to apply all promo discounts.",
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Promo applied."},
    },
    tags=["Dealicious"],
)
def post_promo(
    promo_input: list[dict] = fastapi.Body(
        ..., description=openapi.Descriptions.promo_payload
    ),
    pc_session: python_picnic_api.PicnicAPI = fastapi.Depends(
        picnic_session.get_picnic_client
    ),
) -> None:
    """Looks into the shopping cart to combine discounts.

    Attributes:
        pc_session: The Picnic API session.

    Returns:
        200: Promo applied.

    """
    return controller.post_promo(promo_input=promo_input, pc_session=pc_session)
