from __future__ import annotations

import inspect
from typing import Dict

from botocore.exceptions import BotoCoreError, ClientError
from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from faststream.rabbit import RabbitBroker
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from ..infrastructure.database import get_async_session
from ..infrastructure.rabbit_client import get_rabbit_broker
from ..infrastructure.s3_client import S3Client, get_s3_client
from ..schemas.endpoint import HealthStatus

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
    session_context: AsyncSession = Depends(get_async_session),
    s3_client: S3Client = Depends(get_s3_client),
    broker: RabbitBroker = Depends(get_rabbit_broker),
) -> JSONResponse:
    checks: Dict[str, str] = {}
    status_code = status.HTTP_200_OK

    # Database connectivity check
    try:
        async with session_context as session:
            await session.execute(text("SELECT 1"))
        checks["database"] = "ok"
    except Exception as exc:
        checks["database"] = f"error: {exc.__class__.__name__}"
        status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    # Object storage check
    try:
        await s3_client.get_bucket_list()
        checks["object_storage"] = "ok"
    except (ClientError, BotoCoreError, AssertionError) as exc:
        checks["object_storage"] = f"error: {exc.__class__.__name__}"
        status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    # Message broker check
    try:
        is_connected = getattr(broker, "is_connected", False)
        if not is_connected:
            connect_result = broker.connect()
            if inspect.isawaitable(connect_result):
                await connect_result
            is_connected = getattr(broker, "is_connected", True)
        if is_connected is False:
            raise RuntimeError("Message broker not connected")
        checks["message_broker"] = "ok"
    except Exception as exc:
        checks["message_broker"] = f"error: {exc.__class__.__name__}"
        status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    finally:
        stop_result = broker.stop()
        if inspect.isawaitable(stop_result):
            await stop_result

    overall_status = "ready" if status_code == status.HTTP_200_OK else "not ready"
    payload = HealthStatus(status=overall_status, details=checks)
    return JSONResponse(status_code=status_code, content=payload.model_dump())
