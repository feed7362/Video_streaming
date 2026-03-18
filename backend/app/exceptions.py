import logging

from fastapi import Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from src.core.base_error import AppError


def register_exception_handlers(app):
    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
        """Dynamically handle all AppError exceptions."""
        logging.error(f"{exc.__class__.__name__}: {exc.code} - {exc.message}")
        return JSONResponse(
            status_code=exc.status_code,
            content=jsonable_encoder({"code": exc.code, "message": exc.message}),
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
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        errors = []
        for err in exc.errors():
            errors.append(
                {
                    "loc": ".".join(str(loc) for loc in err.get("loc", [])),
                    "msg": err.get("msg"),
                    "type": err.get("type"),
                }
            )
        logging.exception(f"Unhandled validation error: {errors}")

        return JSONResponse(
            status_code=400,
            content={
                "status": "error",
                "code": 400,
                "message": "Validation failed",
                "errors": errors,
            },
        )
