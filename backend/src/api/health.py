from fastapi import APIRouter
from fastapi.responses import JSONResponse

router_health = APIRouter(
    prefix="/api/health",
    tags=["health_check"],
    default_response_class=JSONResponse,
    responses={
        404: {"description": "Not found"},
        500: {"description": "Internal server error"},
    },
)


@router_health.get("/live")
async def perform_liveness_checks() -> JSONResponse:
    return JSONResponse({"status": "ok"})


# @router_health.get("/ready")
# async def readiness_check():
#     # Example: check DB connectivity
#     db_ok = True
#     if db_ok:
#         return JSONResponse({"status": "ready"})
#     return JSONResponse({"status": "not ready"}, status_code=503)
