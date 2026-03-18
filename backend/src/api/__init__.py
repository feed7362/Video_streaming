from .auth import router_auth
from .dependencies import get_rate_limiter, limit_requests
from .files import router_files
from .health import router_health
from .metrics import router_metrics
from .search import router_search
from .videos import router_videos

__all__ = [
    "get_rate_limiter",
    "limit_requests",
    "router_auth",
    "router_health",
    "router_videos",
    "router_files",
    "router_metrics",
    "router_search",
]
