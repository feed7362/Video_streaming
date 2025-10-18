from __future__ import annotations

import inspect
from typing import Dict

from botocore.exceptions import BotoCoreError, ClientError
from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from ..infrastructure.database import get_async_session
from ..infrastructure.rabbit_client import get_rabbit_broker
from ..infrastructure.s3_client import get_s3_client
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
async def readiness_check() -> JSONResponse:
    checks: Dict[str, str] = {}
    status_code = status.HTTP_200_OK

    # Database connectivity check
    try:
        async with get_async_session() as session:
            await session.execute(text("SELECT 1"))
        checks["database"] = "ok"
    except (SQLAlchemyError, AssertionError) as exc:
        checks["database"] = f"error: {exc.__class__.__name__}"
        status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    except Exception as exc:  # pragma: no cover - defensive guard
        checks["database"] = f"error: {exc.__class__.__name__}"
        status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    # Object storage availability check
    try:
        s3_client = get_s3_client()
        await s3_client.get_bucket_list()
        checks["object_storage"] = "ok"
    except AssertionError as exc:
        checks["object_storage"] = f"misconfigured: {exc}"
        status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    except (ClientError, BotoCoreError) as exc:
        checks["object_storage"] = f"error: {exc.__class__.__name__}"
        status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    except Exception as exc:  # pragma: no cover - defensive guard
        checks["object_storage"] = f"error: {exc.__class__.__name__}"
        status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    # Message broker connectivity check
    broker = None
    newly_connected = False
    try:
        broker = get_rabbit_broker()
        is_connected = getattr(broker, "is_connected", None)
        if not is_connected:
            connect_result = broker.connect()
            if inspect.isawaitable(connect_result):
                await connect_result
            newly_connected = True
            is_connected = getattr(broker, "is_connected", True)
        if is_connected is False:
            raise RuntimeError("Message broker not connected")
        checks["message_broker"] = "ok"
    except Exception as exc:
        checks["message_broker"] = f"error: {exc.__class__.__name__}"
        status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    finally:
        if broker is not None and newly_connected:
            close_result = broker.stop()
            if inspect.isawaitable(close_result):
                await close_result

    overall_status = "ready" if status_code == status.HTTP_200_OK else "not ready"
    payload = HealthStatus(status=overall_status, details=checks)
    return JSONResponse(status_code=status_code, content=payload.model_dump())
