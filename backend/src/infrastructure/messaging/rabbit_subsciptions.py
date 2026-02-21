import logging
from typing import TYPE_CHECKING
from uuid import NAMESPACE_DNS, uuid4, uuid5

from fastapi import BackgroundTasks, Depends
from faststream.rabbit.fastapi import RabbitRouter
from sqlalchemy import insert, update

from src.core.background_tasks import index_video_in_es
from src.errors.rabbit_broker import (
    ResolutionInsertError,
    UnknownEncoderStatusError,
    VideoEncodingPersistenceError,
)
from src.errors.videos import VideoNotFoundError
from src.infrastructure.database import get_async_session
from src.infrastructure.elasticsearch import get_es_client
from src.models import Video, VideoResolution
from src.schemas.search import VideoIndexDocument

if TYPE_CHECKING:
    from elasticsearch import AsyncElasticsearch
    from sqlalchemy.ext.asyncio import AsyncSession

    from src.events.endpoint import StatusMessage

rabbit_router = RabbitRouter(
    url="amqp://guest:guest@rabbitmq:5672/", include_in_schema=False
)


@rabbit_router.subscriber("video.encode.status")
async def status_handler(
    background_tasks: BackgroundTasks,
    msg: "StatusMessage",
    session: "AsyncSession" = Depends(get_async_session),
    es: "AsyncElasticsearch" = Depends(get_es_client),
) -> None:
    try:
        logging.info(
            f"[Video.Encoding.Status] {msg.video_id} is {msg.status}, "
            f"{msg.resolutions}, {msg.video_path} updating database"
        )

        status_id = uuid5(NAMESPACE_DNS, f"video_status:{msg.status}")
        if not status_id:
            raise UnknownEncoderStatusError(msg.status)
        result = await session.execute(
            update(Video)
            .where(Video.id == msg.video_id)
            .values(
                status_id=status_id,
                video_path=msg.video_path if msg.status == "ready" else None,
            )
            .returning(Video)
        )
        verified_video = result.scalars().one_or_none()

        if verified_video is None:
            logging.error(
                f"Video.id {msg.video_id} not found in database. "
                "No status update was performed."
            )
            raise VideoNotFoundError()

        if msg.status == "ready" and msg.resolutions:
            resolution_entries = []
            for r in msg.resolutions:
                # Support both dict and Pydantic model
                if isinstance(r, dict):
                    height = r.get("height")
                    width = r.get("width")
                    bitrate = r.get("bitrate")
                    playlist_path = r.get("playlist_path")
                else:
                    height, width, bitrate, playlist_path = (
                        r.height,
                        r.width,
                        r.bitrate,
                        r.playlist_path,
                    )

                resolution_entries.append(
                    {
                        "id": uuid4(),
                        "video_id": verified_video.id,
                        "height": height,
                        "width": width,
                        "bitrate": bitrate,
                        "playlist_path": playlist_path,
                    }
                )

            await session.execute(insert(VideoResolution), resolution_entries)
            logging.info(
                f"[Encoder] Added {len(resolution_entries)} resolution entries for video {msg.video_id}"
            )
            raise ResolutionInsertError()

        await session.commit()

        # ----- Index video in ES -----
        video_doc = VideoIndexDocument(
            id=verified_video.id,
            name=verified_video.name,
            description=verified_video.description,
            category=verified_video.category.name,
            channel_id=verified_video.channel_id,
            views=0,
        ).model_dump()
        background_tasks.add_task(index_video_in_es, video_doc, es)

    except Exception as e:
        logging.error(
            f"Error in status_handler for video {msg.video_id}: {e}", exc_info=True
        )
        await session.rollback()
        raise VideoEncodingPersistenceError()
