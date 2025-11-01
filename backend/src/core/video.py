import uuid
from typing import Type, TypeVar
from uuid import UUID

from sqlalchemy import delete, func, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..models import CommentReaction, ReactionType
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


#
#
# async def get_video_reaction(
#     video_id: uuid.UUID, session: AsyncSession
# ) -> tuple[int, int]:
#     """Return (likes_count, dislikes_count)."""
#     likes_count = await session.scalar(
#         select(func.count()).where(
#             VideoReaction.video_id == video_id,
#             VideoReaction.is_like.is_(True),
#         )
#     )
#     dislikes_count = await session.scalar(
#         select(func.count()).where(
#             VideoReaction.video_id == video_id,
#             VideoReaction.is_like.is_(False),
#         )
#     )
#     return likes_count, dislikes_count


async def get_video_views(video_id: uuid.UUID, session: AsyncSession) -> int:
    """Return (views_count)."""
    views_count = await session.scalar(
        select(func.count()).where(VideoView.video_id == video_id)
    )
    return views_count


async def toggle_reaction(
    session: AsyncSession,
    user_id: uuid.UUID,
    target_model: Type[VideoReaction] | Type[CommentReaction],
    target_field,  # target_model.video_id or target_model.comment_id
    target_id: uuid.UUID,
    reaction_name: str,  # e.g. "like" or "love"
):
    """Toggle reaction for a user on a video or comment."""

    reaction_type_id = await session.scalar(
        select(ReactionType.id).where(ReactionType.name == reaction_name)
    )
    if not reaction_type_id:
        raise ValueError(f"Unknown reaction type '{reaction_name}'")

    # Check if the user already reacted
    stmt = select(target_model).where(
        target_model.user_id == user_id,
        target_field == target_id,
    )
    existing = await session.scalar(stmt)

    # Remove existing reaction if same type (toggle off)
    if existing and existing.reaction_type_id == reaction_type_id:
        await session.execute(
            delete(target_model).where(target_model.id == existing.id)
        )

    # Update to new reaction type if different
    elif existing:
        await session.execute(
            update(target_model)
            .where(target_model.id == existing.id)
            .values(reaction_type_id=reaction_type_id)
        )
    # Create new reaction if none
    else:
        session.add(
            target_model(
                user_id=user_id,
                reaction_type_id=reaction_type_id,
                **{target_field.key: target_id},
            )
        )

    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise

    # Count all reactions for this target
    result = await session.execute(
        select(ReactionType.name, func.count())
        .join(target_model, target_model.reaction_type_id == ReactionType.id)
        .where(target_field == target_id)
        .group_by(ReactionType.name)
    )
    counts = {name: count for name, count in result.all()}
    return counts


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
