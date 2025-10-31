import uuid
from typing import Type, TypeVar, Union
from uuid import UUID

from sqlalchemy import ColumnElement, func, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import InstrumentedAttribute, selectinload

from ..models.video import Video
from ..models.video_reactions import VideoReaction
from ..models.video_resolutions import VideoResolution
from ..models.video_views import VideoView

T = TypeVar("T", bound=VideoReaction)


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


async def get_video_reaction(
    video_id: uuid.UUID, session: AsyncSession
) -> tuple[int, int]:
    """Return (likes_count, dislikes_count)."""
    likes_count = await session.scalar(
        select(func.count()).where(
            VideoReaction.video_id == video_id,
            VideoReaction.is_like.is_(True),
        )
    )
    dislikes_count = await session.scalar(
        select(func.count()).where(
            VideoReaction.video_id == video_id,
            VideoReaction.is_like.is_(False),
        )
    )
    return likes_count, dislikes_count


async def get_video_views(video_id: uuid.UUID, session: AsyncSession) -> int:
    """Return (views_count)."""
    views_count = await session.scalar(
        select(func.count()).where(VideoView.video_id == video_id)
    )
    return views_count


async def toggle_reaction(
    session: AsyncSession,
    like_model: Type[T],
    target_id_field: Union[InstrumentedAttribute, ColumnElement],
    target_id: uuid.UUID,
    user_id: uuid.UUID,
    is_like: bool,
):
    """
    Generic helper to toggle like/dislike for any model.

    Returns: (likes_count, dislikes_count)
    """

    # Check if the user already liked/disliked this target
    existing = await session.scalar(
        select(like_model).where(
            target_id_field == target_id,
            like_model.user_id == user_id,
        )
    )

    # Update or insert new like/dislike
    if existing:
        existing.is_like = is_like
    else:
        new_like = like_model(
            user_id=user_id,
            **{target_id_field.key: target_id},
            is_like=is_like,
        )
        session.add(new_like)

    await session.commit()

    # Count total likes and dislikes
    likes_count = await session.scalar(
        select(func.count()).where(
            target_id_field == target_id, like_model.is_like.is_(True)
        )
    )
    dislikes_count = await session.scalar(
        select(func.count()).where(
            target_id_field == target_id, like_model.is_like.is_(False)
        )
    )

    return likes_count, dislikes_count


async def record_video_view(
    session: AsyncSession,
    video_id: UUID,
    user_id: UUID | None = None,
) -> None:
    """
    Record a unique view for a video.
    Increments views_count only if user hasn't viewed it before.
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
