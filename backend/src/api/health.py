from __future__ import annotations

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from ..schemas.endpoint import HealthStatus
from ..services.health import HealthService
from .dependencies.services import get_health_service

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
    service: HealthService = Depends(get_health_service),
) -> JSONResponse:
    payload = await service.check_health()
    return JSONResponse(status_code=service.status_code, content=payload.model_dump())
