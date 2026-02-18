import uuid
from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import func, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..models.video import Video
from ..models.video_resolutions import VideoResolution
from ..models.video_views import VideoView

if TYPE_CHECKING:
    from faststream.rabbit import RabbitBroker

    from ..infrastructure.s3_client import S3Client


async def get_video_by_id(
    video_id: uuid.UUID,
    session: AsyncSession,
) -> tuple[Video | None, list[str]]:
    """
    Fetch a video with related data (channel, privacy, resolutions).

    Returns (video, resolutions)
    """
    stmt = (
        select(Video)
        .where(Video.id == video_id)
        .options(
            selectinload(Video.channel),
            selectinload(Video.privacy),
            selectinload(Video.resolutions),
        )
    )

    result = await session.execute(stmt)
    video = result.scalars().first()
    if not video:
        return None, []

    # Collect resolution labels like ["360p", "720p", ...]
    result = await session.execute(
        select(VideoResolution.height).where(VideoResolution.video_id == video_id)
    )
    heights = result.scalars().all()
    resolutions = [f"{h}p" for h in heights]

    return video, resolutions


async def get_video_views(video_id: uuid.UUID, session: AsyncSession) -> int:
    """Return (views_count)."""
    views_count = await session.scalar(
        select(func.count()).where(VideoView.video_id == video_id)
    )
    return views_count or 0


async def record_video_view(
    session: AsyncSession,
    video_id: UUID,
    user_id: UUID | None = None,
) -> None:
    """
    Record a unique view for a video.
    Increments views_count only if the user hasn't viewed it before.
    """
    stmt = select(VideoView.id).where(
        VideoView.video_id == video_id,
        VideoView.user_id == user_id,
    )
    existing = await session.scalar(stmt)
    if existing:
        return

    view = VideoView(video_id=video_id, user_id=user_id)
    session.add(view)

    await session.execute(
        update(Video)
        .where(Video.id == video_id)
        .values(views_count=Video.views_count + 1)
    )

    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()


class VideoService:
    def __init__(
        self,
        session: AsyncSession,
        s3_client: "S3Client",
        broker: Optional["RabbitBroker"] = None,
    ):
        self.session = session
        self.s3_client = s3_client
        self.broker = broker
