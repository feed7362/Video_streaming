from typing import TYPE_CHECKING
from uuid import UUID

from fastapi import Depends

from src.infrastructure import (
    get_async_session,
    get_es_client,
    get_rabbit_broker,
    get_s3_client,
)
from src.services import get_current_user_id
from src.services.analytics import AnalyticsService
from src.services.comments import CommentService
from src.services.file_signing import FileSigningService
from src.services.files import FileService
from src.services.health import HealthService
from src.services.search import SearchService
from src.services.videos import VideoService

if TYPE_CHECKING:
    from elasticsearch import AsyncElasticsearch
    from faststream.rabbit import RabbitBroker
    from sqlalchemy.ext.asyncio import AsyncSession

    from src.infrastructure.s3_client import S3Client


def get_video_service(
    session: "AsyncSession" = Depends(get_async_session),
) -> VideoService:
    return VideoService(session)


def get_comment_service(
    session: "AsyncSession" = Depends(get_async_session),
) -> CommentService:
    return CommentService(session)


def get_file_service(
    session: "AsyncSession" = Depends(get_async_session),
    s3_client: "S3Client" = Depends(get_s3_client),
    broker: "RabbitBroker" = Depends(get_rabbit_broker),
) -> FileService:
    return FileService(session, s3_client, broker)


def get_file_signing_service(
    s3_client: "S3Client" = Depends(get_s3_client),
) -> FileSigningService:
    return FileSigningService(s3_client)


def get_health_service(
    session: "AsyncSession" = Depends(get_async_session),
    s3_client: "S3Client" = Depends(get_s3_client),
    broker: "RabbitBroker" = Depends(get_rabbit_broker),
) -> HealthService:
    return HealthService(session, s3_client, broker)


def get_search_service(
    es: "AsyncElasticsearch" = Depends(get_es_client),
) -> SearchService:
    return SearchService(es)


async def get_service_and_channel(
    user_id: UUID = Depends(get_current_user_id),
    session: "AsyncSession" = Depends(get_async_session),
) -> tuple[AnalyticsService, object]:
    service = AnalyticsService(session)
    channel = await service.get_channel(user_id)
    return service, channel
