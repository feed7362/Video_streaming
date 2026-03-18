from fastapi import APIRouter
from fastapi.responses import JSONResponse, Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

router_metrics = APIRouter(
    prefix="/api/metrics",
    tags=["monitoring"],
    default_response_class=JSONResponse,
    responses={
        404: {"description": "Not found"},
        500: {"description": "Internal server error"},
    },
)


@router_metrics.get(
    "/",
    include_in_schema=True,
    summary="Retrieve Prometheus metrics",
    description=(
        "Expose the application's Prometheus-formatted metrics for scraping by "
        "monitoring systems."
    ),
    response_description="Plain text payload containing Prometheus metrics.",
    responses={
        200: {
            "description": "Successful metrics response",
            "content": {
                "text/plain; version=0.0.4": {
                    "schema": {
                        "type": "string",
                        "example": "# HELP http_requests_total Total HTTP requests",
                    }
                }
            },
        }
    },
    response_class=Response,
)
async def get_metrics_doc() -> Response:
    """
    Prometheus metrics endpoint
    """
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
