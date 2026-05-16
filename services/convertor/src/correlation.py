"""Mirror of bff's correlation plumbing for the convertor worker.

Consumers call set_request_id(...) at the top of each handler with the
correlation_id read from the incoming RabbitMQ message; every log line during
that task carries the same rid as the originating HTTP request.
"""

import logging
from contextvars import ContextVar

_request_id_var: ContextVar[str] = ContextVar("request_id", default="-")


def get_request_id() -> str:
    return _request_id_var.get()


def set_request_id(value: str) -> None:
    _request_id_var.set(value or "-")


class RequestIdLogFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = _request_id_var.get()
        return True


def install_log_filter() -> None:
    f = RequestIdLogFilter()
    root = logging.getLogger()
    if not any(isinstance(x, RequestIdLogFilter) for x in root.filters):
        root.addFilter(f)
    for h in root.handlers:
        if not any(isinstance(x, RequestIdLogFilter) for x in h.filters):
            h.addFilter(f)
