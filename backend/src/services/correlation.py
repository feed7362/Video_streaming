"""Request-correlation ID plumbing.

Flow:
  HTTP request → CorrelationIdMiddleware reads/creates X-Request-ID, sets
  contextvar → handlers can call get_request_id() → broker.publish() forwards
  it as the message correlation_id → convertor reads it and logs with it.
"""

import logging
import uuid
from contextvars import ContextVar

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.types import ASGIApp

REQUEST_ID_HEADER = "x-request-id"
_request_id_var: ContextVar[str] = ContextVar("request_id", default="-")


def get_request_id() -> str:
    return _request_id_var.get()


def set_request_id(value: str) -> None:
    _request_id_var.set(value)


class RequestIdLogFilter(logging.Filter):
    """Injects request_id into every log record so formatters can use %(request_id)s."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = _request_id_var.get()
        return True


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        rid = request.headers.get(REQUEST_ID_HEADER) or uuid.uuid4().hex
        token = _request_id_var.set(rid)
        try:
            response = await call_next(request)
        finally:
            _request_id_var.reset(token)
        response.headers[REQUEST_ID_HEADER] = rid
        return response


def install_log_filter() -> None:
    """Attach the filter to the root logger so all logs carry request_id."""
    f = RequestIdLogFilter()
    root = logging.getLogger()
    if not any(isinstance(x, RequestIdLogFilter) for x in root.filters):
        root.addFilter(f)
    # Also attach to handlers so it survives propagation tweaks.
    for h in root.handlers:
        if not any(isinstance(x, RequestIdLogFilter) for x in h.filters):
            h.addFilter(f)
