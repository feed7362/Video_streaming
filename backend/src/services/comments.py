from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.core.pagination import paginate_query
from src.errors.comments import (
    CommentDeleteForbiddenError,
    CommentNotFoundError,
    ParentCommentNotFoundError,
    ParentCommentVideoMismatchError,
)
from src.errors.videos import VideoNotFoundError
from src.models import Comment, CommentReaction, Video
from src.schemas.comments import to_comment_read
from src.services.reactions import toggle_reaction


class CommentService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_video(self, video_id: UUID, page: int, size: int):
        filters = [Comment.video_id == video_id]
        preload = [selectinload(Comment.user)]

        return await paginate_query(
            session=self.session,
            model=Comment,
            page=page,
            size=size,
            filters=filters,
            order_by=Comment.created_at.desc(),
            preload=preload,
            mapper=to_comment_read,
        )

    async def create(
        self, video_id: UUID, user_id: UUID, content: str, parent_id: UUID | None
    ):
        # 1. Validate Video
        video = await self.session.scalar(select(Video).where(Video.id == video_id))
        if not video:
            raise VideoNotFoundError()

        # 2. Validate Parent Comment
        if parent_id:
            parent = await self.session.scalar(
                select(Comment).where(Comment.id == parent_id)
            )
            if not parent:
                raise ParentCommentNotFoundError()

            if parent.video_id != video_id:
                raise ParentCommentVideoMismatchError()

        # 3. Create
        comment = Comment(
            video_id=video_id,
            user_id=user_id,
            content=content,
            parent_id=parent_id,
            created_at=datetime.now(),
        )
        self.session.add(comment)
        await self.session.commit()

        # 4. Refresh for response
        await self.session.refresh(comment, attribute_names=["user"])
        return to_comment_read(comment)

    async def delete(self, comment_id: UUID, user_id: UUID) -> None:
        # Fetch comment with video channel info for ownership check
        result = await self.session.execute(
            select(Comment)
            .options(selectinload(Comment.video).selectinload(Video.channel))
            .where(Comment.id == comment_id)
        )
        comment = result.scalar_one_or_none()

        if not comment:
            raise CommentNotFoundError()

        # Authorization: Author OR Video Owner
        is_author = comment.user_id == user_id
        is_video_owner = comment.video.channel.user_id == user_id

        if not (is_author or is_video_owner):
            raise CommentDeleteForbiddenError()

        await self.session.delete(comment)
        await self.session.commit()

    async def react(self, comment_id: UUID, user_id: UUID, reaction_name: str) -> dict:
        return await toggle_reaction(
            session=self.session,
            user_id=user_id,
            target_model=CommentReaction,
            target_field=CommentReaction.comment_id,
            target_id=comment_id,
            reaction_name=reaction_name,
        )
