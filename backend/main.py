import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.files import router_files
from src.api.health import router_health
from src.api.metrics import PrometheusMiddleware, router_metrics
from src.i18n import LanguageMiddleware
from src.services.rabbit_client import rabbit_broker
from src.services.s3_client import get_s3_client


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    await rabbit_broker.connect()

    s3_client = get_s3_client()
    await s3_client.check_bucket_exists()
    logging.info("Startup complete. Metrics exposed.")
    yield
    logging.info("Shutdown complete.")
    await rabbit_broker.close()


def create_app(use_lifespan: bool = True) -> FastAPI:
    lifespan_ctx = lifespan if use_lifespan else None
    app = FastAPI(
        title="My API", description="BFF", version="1.0.0", lifespan=lifespan_ctx
    )

    app.include_router(router_health)
    app.include_router(router_files)
    app.include_router(router_metrics)
    app.add_middleware(LanguageMiddleware)
    app.add_middleware(PrometheusMiddleware)

    origins = [
        "http://localhost",
        "http://localhost:8000",
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    return app


app = create_app()
