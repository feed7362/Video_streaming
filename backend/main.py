from fastapi import FastAPI

from app import add_middlewares, include_routers, lifespan, register_exception_handlers


def create_app(use_lifespan: bool = True) -> FastAPI:
    lifespan_ctx = lifespan if use_lifespan else None
    main_app = FastAPI(
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
    include_routers(main_app)
    add_middlewares(main_app)
    register_exception_handlers(main_app)

    return main_app


app = create_app()
