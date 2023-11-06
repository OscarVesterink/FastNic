""" Contains endpoints for performing health checks of the service."""
import fastapi
from fastapi import status
import python_picnic_api

from src.routers.health import controller
from src.picnic import session as picnic_session

router = fastapi.APIRouter(prefix="/health", tags=["Health"])


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    summary="Endpoint for health checks of the service.",
    description="This endpoint can be used to check whether the service is up. "
    "It returns an empty response.",
)
def health_check() -> None:
    """Performs a service health check. Takes in nothing, returns None."""
    pass


@router.get(
    "/picnic",
    status_code=status.HTTP_200_OK,
    summary="Endpoint for health checks of the connection to Picnic.",
    description="This endpoint can be used to check whether the service is connected "
    "to Picnic. It returns a boolean.",
    response_model=bool,
)
def picnic_check(
    pc_session: python_picnic_api.PicnicAPI = fastapi.Depends(
        picnic_session.get_picnic_client
    ),
) -> bool:
    """Performs a health check of the connections to Picnic.

    Returns:
        True if the connection is successful, False otherwise.
    """
    return controller.check_picnic_connection(pc_session=pc_session)
