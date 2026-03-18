from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.database import get_async_session
from src.schemas.analytics import AudienceResponse, ContentResponse, OverviewResponse
from src.services.analytics import AnalyticsService
from src.services.auth import get_current_user_id

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


async def _get_service_and_channel(
    user_id: UUID = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_async_session),
) -> tuple[AnalyticsService, object]:
    service = AnalyticsService(session)
    channel = await service.get_channel(user_id)
    if channel is None:
        raise HTTPException(status_code=404, detail="No channel found for this user")
    return service, channel


@router_analytics.get("/overview", response_model=OverviewResponse)
async def analytics_overview(
    deps: tuple = Depends(_get_service_and_channel),
) -> OverviewResponse:
    service, channel = deps
    return await service.get_overview(channel)


@router_analytics.get("/content", response_model=ContentResponse)
async def analytics_content(
    deps: tuple = Depends(_get_service_and_channel),
) -> ContentResponse:
    service, channel = deps
    return await service.get_content(channel)


@router_analytics.get("/audience", response_model=AudienceResponse)
async def analytics_audience(
    deps: tuple = Depends(_get_service_and_channel),
) -> AudienceResponse:
    service, channel = deps
    return await service.get_audience(channel)
