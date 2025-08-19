# import asyncio
# import time
# from typing import Dict, Any, Awaitable, Callable
from fastapi.responses import Response
from fastapi import APIRouter

router_health = APIRouter(
    prefix="/api/health",
    tags=["health_check"]
)

#
# CHECKS: Dict[str, Callable[..., Awaitable[Dict[str, Any]]]] = {
#     "database": lambda settings: check_database(settings.database_url, settings.health_check_timeout),
#     "redis": lambda settings: check_redis(settings.redis_url, settings.health_check_timeout),
#     "s3": lambda settings: check_s3(settings.s3_url, settings.health_check_timeout),
# }
#
#
# @router_health.get("/ready")
# async def perform_readiness_checks(settings: "Settings" = Depends()) -> Dict[str, Any]:
#     tasks = {
#         name: checker(settings)
#         for name, checker in CHECKS.items()
#         if getattr(settings, f"{name}_url", None)
#     }
#
#     results = await asyncio.gather(*tasks.values(), return_exceptions=True)
#
#     checks: Dict[str, Any] = {}
#     for name, result in zip(tasks.keys(), results):
#         if isinstance(result, Exception):
#             checks[name] = {"status": "unhealthy", "error": str(result)}
#         else:
#             checks[name] = result
#
#     overall_status = "healthy" if all(c["status"] == "healthy" for c in checks.values()) else "unhealthy"
#
#     return {
#         "status": overall_status,
#         "timestamp": time.time(),
#         "checks": checks,
#     }


@router_health.get("/live")
async def perform_liveness_checks():
    return Response(status_code=200)
