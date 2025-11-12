import logging
from uuid import NAMESPACE_DNS, uuid4, uuid5

from fastapi import Depends
from faststream.rabbit.fastapi import RabbitRouter
from sqlalchemy import insert, update
from sqlalchemy.ext.asyncio import AsyncSession

from ..infrastructure.database import get_async_session
from ..models import Video, VideoResolution
from ..schemas.endpoint import StatusMessage

rabbit_router = RabbitRouter(
    url="amqp://guest:guest@rabbitmq:5672/", include_in_schema=False
)


@rabbit_router.subscriber("video.encode.status")
async def status_handler(
    msg: StatusMessage, session: AsyncSession = Depends(get_async_session)
) -> None:
    try:
        logging.info(
            f"[Video.Encoding.Status] {msg.video_id} is {msg.status}, "
            f"{msg.resolutions}, {msg.video_path} updating database"
        )

        status_id = uuid5(NAMESPACE_DNS, f"video_status:{msg.status}")
        if not status_id:
            logging.warning(f"Unknown encoder status: {msg.status}")
            return
        result = await session.execute(
            update(Video)
            .where(Video.id == msg.video_id)
            .values(
                status_id=status_id,
                video_path=msg.video_path if msg.status == "ready" else None,
            )
            .returning(Video.id)
            .execution_options(synchronize_session="fetch")
        )
        verified_id = result.scalar_one_or_none()

        if verified_id is None:
            logging.error(
                f"Video.id {msg.video_id} not found in database. "
                "No status update was performed."
            )

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
                        "video_id": verified_id,
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

        await session.commit()
    except Exception as e:
        logging.error(
            f"Error in status_handler for video {msg.video_id}: {e}", exc_info=True
        )
        await session.rollback()
        raise
