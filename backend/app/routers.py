from src.api.auth import router_auth
from src.api.comments import router_comments
from src.api.files import router_files
from src.api.health import router_health
from src.api.metrics import router_metrics
from src.api.search import router_search
from src.api.videos import router_videos
from src.infrastructure.messaging.rabbit_subsciptions import rabbit_router


def include_routers(app):
    app.include_router(router_health)
    app.include_router(router_files)
    app.include_router(router_metrics)
    app.include_router(router_videos)
    app.include_router(router_comments)
    app.include_router(rabbit_router)
    app.include_router(router_search)
    app.include_router(router_auth)
