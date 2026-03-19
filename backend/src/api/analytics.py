from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from src.api.dependencies.services import get_service_and_channel
from src.schemas.analytics import AudienceResponse, ContentResponse, OverviewResponse

router_analytics = APIRouter(
    prefix="/api/analytics",
    tags=["analytics"],
    default_response_class=JSONResponse,
    responses={
        401: {"description": "Not authenticated"},
        404: {"description": "Channel not found"},
        500: {"description": "Internal server error"},
    },
)


@router_analytics.get("/overview", response_model=OverviewResponse)
async def analytics_overview(
    deps: tuple = Depends(get_service_and_channel),
) -> OverviewResponse:
    service, channel = deps
    return await service.get_overview(channel)


@router_analytics.get("/content", response_model=ContentResponse)
async def analytics_content(
    deps: tuple = Depends(get_service_and_channel),
) -> ContentResponse:
    service, channel = deps
    return await service.get_content(channel)


@router_analytics.get("/audience", response_model=AudienceResponse)
async def analytics_audience(
    deps: tuple = Depends(get_service_and_channel),
) -> AudienceResponse:
    service, channel = deps
    return await service.get_audience(channel)
