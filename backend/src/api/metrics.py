import time
from typing import List, Callable
from fastapi import Request, APIRouter
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response
from starlette.middleware.base import BaseHTTPMiddleware
from ..schemas.metric import (
    REQUEST_DURATION_HIST,
    REQUESTS_IN_PROGRESS,
    EXCEPTIONS_TOTAL,
    RESPONSES_TOTAL,
)

router_metrics = APIRouter(
    prefix="/api/metrics",
    tags=["monitoring"]
)


@router_metrics.get("", include_in_schema=True)
async def get_metrics_doc():
    """
    Prometheus metrics endpoint
    """
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


EXCLUDE_PATH_PREFIXES: List[str] = [
    "/api/metrics", "/api/health", "/static", "/docs", "/openapi.json", "/redoc"
]


def is_excluded_path(path: str) -> bool:
    return any(path.startswith(p) for p in EXCLUDE_PATH_PREFIXES)


class PrometheusMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable):

        if is_excluded_path(request.url.path):
            return await call_next(request)

        route = request.scope.get("route")
        if route and hasattr(route, "path"):
            path_label = route.path
        else:
            path_label = request.url.path

        method = request.method

        REQUESTS_IN_PROGRESS.labels(method=method, path=path_label).inc()
        start = time.perf_counter()

        try:
            response = await call_next(request)
            status_code = str(response.status_code)

            RESPONSES_TOTAL.labels(status_code=status_code, method=method, path=path_label).inc()
            return response
        except Exception as exc:
            exc_type = type(exc).__name__
            EXCEPTIONS_TOTAL.labels(exception_type=exc_type, method=method, path=path_label).inc()
            raise
        finally:
            duration = time.perf_counter() - start
            REQUEST_DURATION_HIST.labels(method=method, path=path_label).observe(duration)
            REQUESTS_IN_PROGRESS.labels(method=method, path=path_label).dec()
