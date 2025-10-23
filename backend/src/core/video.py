import uuid
from typing import Any, Type, TypeVar, Union

from sqlalchemy import ColumnElement, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import InstrumentedAttribute

from ..models.hls_files import HLSFile
from ..models.video import Video
from ..models.video_reactions import VideoReaction
from ..models.video_views import VideoView

T = TypeVar("T", bound=VideoReaction)


async def get_video_by_id(
    video_id: uuid.UUID, session: AsyncSession
) -> tuple[None, list[Any]] | tuple[Video, list[str]]:
    """Fetch a video and all associated HLS resolutions."""
    video = await session.scalar(select(Video).where(Video.id == video_id))
    if not video:
        return None, []

    # Query all resolutions for this video
    result = await session.scalars(
        select(HLSFile.resolution).where(HLSFile.video_id == video_id)
    )
    resolutions = list(result.all())

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
