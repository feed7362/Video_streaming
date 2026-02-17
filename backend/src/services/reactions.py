import uuid
from typing import Type

from sqlalchemy import delete, func, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import InstrumentedAttribute

from src.models import CommentReaction, ReactionType
from src.models.video_reactions import VideoReaction


async def toggle_reaction(
    session: AsyncSession,
    user_id: uuid.UUID,
    target_model: Type[VideoReaction] | Type[CommentReaction],
    target_field: InstrumentedAttribute[
        uuid.UUID
    ],  # target_model.video_id or target_model.comment_id
    target_id: uuid.UUID,
    reaction_name: str,  # e.g. "like" or "love"
) -> dict[str, int]:
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

    # Remove the existing reaction if the same type (toggle off)
    if isinstance(existing, (VideoReaction, CommentReaction)):
        if existing and existing.reaction_type_id == reaction_type_id:
            await session.execute(
                delete(target_model).where(target_model.id == existing.id)
            )

        # Update to a new reaction type if different
        elif existing:
            await session.execute(
                update(target_model)
                .where(target_model.id == existing.id)
                .values(reaction_type_id=reaction_type_id)
            )
    # Create a new reaction if none
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
