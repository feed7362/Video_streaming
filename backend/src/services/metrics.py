import time
from typing import Callable, List

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.routing import Match

from src.schemas.metric import (
    EXCEPTIONS_TOTAL,
    REQUEST_DURATION_HIST,
    REQUESTS_IN_PROGRESS,
    REQUESTS_TOTAL,
    RESPONSES_TOTAL,
)

EXCLUDE_PATH_PREFIXES: List[str] = [
    "/api/metrics",
    "/api/health",
    "/static",
    "/docs",
    "/openapi.json",
]

APP_NAME = "FastAPI Video Streaming"


def is_excluded_path(path: str) -> bool:
    return any(path.startswith(p) for p in EXCLUDE_PATH_PREFIXES)


def get_route_path(request: Request) -> str:
    """Safely extract the templated path (e.g., /videos/{id}) to avoid high cardinality."""
    for route in request.app.routes:
        match, _ = route.matches(request.scope)
        if match == Match.FULL:
            return route.path
    return request.url.path


class PrometheusMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if is_excluded_path(request.url.path):
            return await call_next(request)

        path_label = get_route_path(request)
        method = request.method

        REQUESTS_IN_PROGRESS.labels(
            method=method, path=path_label, app_name=APP_NAME
        ).inc()

        start = time.perf_counter()

        try:
            response = await call_next(request)
            status_code = str(response.status_code)

            RESPONSES_TOTAL.labels(
                status_code=status_code,
                method=method,
                path=path_label,
                app_name=APP_NAME,
            ).inc()

            REQUESTS_TOTAL.labels(
                method=method, path=path_label, app_name=APP_NAME
            ).inc()

            return response

        except Exception as exc:
            exc_type = type(exc).__name__
            EXCEPTIONS_TOTAL.labels(
                exception_type=exc_type,
                method=method,
                path=path_label,
                app_name=APP_NAME,
            ).inc()
            raise

        finally:
            duration = time.perf_counter() - start
            REQUEST_DURATION_HIST.labels(
                method=method, path=path_label, app_name=APP_NAME
            ).observe(duration)

            REQUESTS_IN_PROGRESS.labels(
                method=method, path=path_label, app_name=APP_NAME
            ).dec()
