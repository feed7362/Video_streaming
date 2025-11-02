import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.api.files import router_files
from src.api.health import router_health
from src.api.metrics import PrometheusMiddleware, router_metrics
from src.api.videos import router_videos
from src.core.rabbit_subsciptions import rabbit_router
from src.i18n import LanguageMiddleware
from src.infrastructure.database import engine
from src.infrastructure.rabbit_client import rabbit_broker
from src.infrastructure.s3_client import get_s3_client
from utils.db_seeder import seed_initial_data


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    await rabbit_broker.start()
    logging.info("Rabbit broker connected successfully.")
    s3_client = get_s3_client()
    await s3_client.check_bucket_exists()
    await seed_initial_data()
    logging.info("Startup complete. Metrics exposed.")
    yield
    await rabbit_broker.close()
    logging.info("Rabbit broker connection disposed gracefully.")
    await engine.dispose()
    logging.info("Database engine disposed gracefully.")
    logging.info("Shutdown complete.")


def create_app(use_lifespan: bool = True) -> FastAPI:
    lifespan_ctx = lifespan if use_lifespan else None
    app = FastAPI(
        title="Video Streaming BFF",
        description="Backend service powering the video streaming experience.",
        version="1.0.0",
        docs_url="/docs",
        redoc_url=None,
        openapi_url="/openapi.json",
        contact={
            "name": "John Doe",
            "email": "john@example.com",
        },
        license_info={
            "name": "MIT",
        },
        openapi_tags=[
            {
                "name": "files",
                "description": "Endpoints for uploading, streaming, and downloading video files.",
            },
            {
                "name": "health_check",
                "description": "Health check endpoints that provide liveness and readiness status.",
            },
            {
                "name": "monitoring",
                "description": "Prometheus metrics endpoints for operational monitoring.",
            },
        ],
        swagger_ui_parameters={
            "deepLinking": True,
            "defaultModelsExpandDepth": 2,  # show all models and schemas expanded
            "defaultModelExpandDepth": 2,  # expand individual model fields
            "displayRequestDuration": True,
            "displayOperationDuration": True,
            "defaultModelRendering": "example",
            "showMutatedRequest": True,
            "docExpansion": "list",  # expand all tags (groups) by default
            "supportedSubmitMethods": ["get", "post", "put", "delete", "patch"],
            "filter": True,
            "showExtensions": True,  # show any x-* vendor extensions
            "showCommonExtensions": True,  # show standard extensions like x-codeSamples
            "syntaxHighlight": True,  # enable syntax highlighting for request/response
            "requestSnippetsEnabled": True,
        },
        lifespan=lifespan_ctx,
    )

    app.include_router(router_health)
    app.include_router(router_files)
    app.include_router(router_metrics)
    app.include_router(router_videos)
    app.include_router(rabbit_router)
    app.add_middleware(LanguageMiddleware)
    app.add_middleware(PrometheusMiddleware)

    origins = [
        "http://localhost",
        "http://127.0.0.1",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:80",
    ]
  
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "detail": exc.detail or str(exc),
                "status_code": exc.status_code,
                "type": exc.__class__.__name__,
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        logging.exception(f"Unhandled error: {exc}")
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"},
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc) -> JSONResponse:
        return JSONResponse(
            status_code=400,
            content={"detail": str(exc)},
        )

    return app


app = create_app()
