import asyncio
from typing import Dict

from fastapi import APIRouter

router_health = APIRouter(
    prefix="/api/health",
    tags=["health_check"]
)

# @router_health.get("/live")
# async def perform_health_checks(settings: Settings) -> Dict[str, ServiceCheck]:
#     checks = {}
#     tasks = []
#     if settings.database_url:
#         tasks.append(("database", check_database(settings.database_url, settings.health_check_timeout)))
#     if settings.redis_url:
#         tasks.append(("redis", check_redis(settings.redis_url, settings.health_check_timeout)))
#     if tasks:
#         results = await asyncio.gather(*[task[1] for task in tasks], return_exceptions=True)
#     return checks

# {
#   "status": "healthy",
#   "timestamp": 1640995200.123,
#   "version": "1.0.0",
#   "checks": {
#     "database": {
#       "status": "healthy",
#       "duration_ms": 23.4
#     },
#     "redis": {
#       "status": "healthy",
#       "duration_ms": 12.1
#     }
#   }
# }

# @router_health.get("/ready")
