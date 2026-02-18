from fastapi.middleware.cors import CORSMiddleware

from src.i18n import LanguageMiddleware
from src.services.metrics import PrometheusMiddleware


def add_middlewares(app):
    origins = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
        allow_headers=["*"],
    )
    app.add_middleware(LanguageMiddleware)
    app.add_middleware(PrometheusMiddleware)
