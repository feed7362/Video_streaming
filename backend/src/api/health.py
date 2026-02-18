from __future__ import annotations

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from faststream.rabbit import RabbitBroker
from sqlalchemy.ext.asyncio import AsyncSession

from ..infrastructure.database import get_async_session
from ..infrastructure.messaging.client import get_rabbit_broker
from ..infrastructure.s3_client import S3Client, get_s3_client
from ..schemas.endpoint import HealthStatus
from ..services.health import HealthService

router_health = APIRouter(
    prefix="/api/health",
    tags=["health_check"],
    default_response_class=JSONResponse,
    responses={
        404: {"description": "Not found"},
        500: {"description": "Internal server error"},
    },
)


@router_health.get(
    "/live",
    response_model=HealthStatus,
    summary="Liveness probe",
    description="Returns whether the API instance is running.",
    response_description="Current liveness status.",
    responses={
        200: {
            "model": HealthStatus,
            "description": "The service is up and responding.",
        }
    },
)
async def perform_liveness_checks() -> HealthStatus:
    return HealthStatus(status="ok")


@router_health.get(
    "/ready",
    response_model=HealthStatus,
    summary="Readiness probe",
    description=(
        "Checks whether critical dependencies such as the database, object storage, "
        "and message broker are available."
    ),
    response_description="Current readiness status including dependency checks.",
    responses={
        200: {
            "model": HealthStatus,
            "description": "All dependencies are reachable and the service is ready.",
        },
        503: {
            "model": HealthStatus,
            "description": "One or more dependencies are unavailable.",
        },
    },
)
async def readiness_check(
    session: AsyncSession = Depends(get_async_session),
    s3_client: S3Client = Depends(get_s3_client),
    broker: RabbitBroker = Depends(get_rabbit_broker),
) -> JSONResponse:
    service = HealthService(session, s3_client, broker)
    payload = await service.check_health()
    return JSONResponse(status_code=service.status_code, content=payload.model_dump())
