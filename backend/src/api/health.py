from fastapi import APIRouter
from fastapi.responses import Response

router_health = APIRouter(prefix="/api/health", tags=["health_check"])


@router_health.get("/live")
async def perform_liveness_checks() -> Response:
    return Response(status_code=200)
