from fastapi.middleware.cors import CORSMiddleware

from src.i18n import InternationalizationMiddleware
from src.services.correlation import CorrelationIdMiddleware, install_log_filter
from src.services.metrics import PrometheusMiddleware


def add_middlewares(app):
    install_log_filter()

    origins = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
        allow_headers=["*", "X-Request-ID"],
        expose_headers=["X-Request-ID"],
    )
    app.add_middleware(InternationalizationMiddleware)
    app.add_middleware(PrometheusMiddleware)
    # Outermost — runs first on the way in, last on the way out.
    app.add_middleware(CorrelationIdMiddleware)
