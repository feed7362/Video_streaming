from prometheus_client import Counter, Gauge, Histogram

REQUEST_DURATION_HIST = Histogram(
    "fastapi_requests_duration_seconds",
    "Request duration in seconds",
    ["method", "path"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10),
)

REQUESTS_IN_PROGRESS = Gauge(
    "fastapi_requests_in_progress", "Number of in-progress requests", ["method", "path"]
)

EXCEPTIONS_TOTAL = Counter(
    "fastapi_exceptions_total",
    "Total number of unhandled exceptions",
    ["exception_type", "method", "path"],
)

RESPONSES_TOTAL = Counter(
    "fastapi_responses_total",
    "Total number of responses",
    ["status_code", "method", "path"],
)
