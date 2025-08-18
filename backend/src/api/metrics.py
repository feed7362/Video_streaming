from fastapi import Request, APIRouter
from fastapi.responses import RedirectResponse
from prometheus_client import make_asgi_app

metrics_app = make_asgi_app()

router_metrics = APIRouter(
    prefix="/api/metrics",
    tags=["monitoring"]
)


@router_metrics.get("/", include_in_schema=True)
async def get_metrics_doc(request: Request):
    """
    Prometheus metrics endpoint
    """
    return RedirectResponse(url=str(request.url))
