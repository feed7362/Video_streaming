from datetime import datetime
from typing import Generic, List, Optional, TypeVar
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator
from sqlalchemy import inspect as sa_inspect

from src.models import Comment

T = TypeVar("T")


class CommentCreate(BaseModel):
    content: str


class CommentRead(BaseModel):
    id: UUID
    user_id: UUID
    content: str
    created_at: datetime
    likes_count: int
    dislikes_count: int
    parent_id: Optional[UUID] = None
    user_name: str
    user_avatar: Optional[str]
    replies: List["CommentRead"] = []

    model_config = ConfigDict(from_attributes=True)


CommentRead.model_rebuild()


def to_comment_read(c: Comment) -> CommentRead:
    # Only iterate replies if already eagerly loaded — accessing an unloaded
    # lazy relationship inside an async session raises MissingGreenlet.
    state = sa_inspect(c)
    loaded_replies = (
        [to_comment_read(r) for r in c.replies]
        if "replies" not in state.unloaded
        else []
    )
    return CommentRead(
        id=c.id,
        user_id=c.user_id,
        content=c.content,
        created_at=c.created_at,
        likes_count=c.likes_count,
        dislikes_count=c.dislikes_count,
        user_name=getattr(c.user, "name", "Anonymous"),
        user_avatar=getattr(c.user, "avatar_url", None),
        parent_id=c.parent_id,
        replies=loaded_replies,
    )


class Page(BaseModel, Generic[T]):
    items: List[T]
    page: int
    size: int
    total: int


class CommentPage(Page[CommentRead]):
    """Paginated list of comments."""

    pass


class OwnerCommentRead(BaseModel):
    """Comment shape for the creator moderation view — includes the parent
    video so the table can show which video each comment belongs to."""

    id: UUID
    user_id: UUID
    user_name: str
    user_avatar: Optional[str] = None
    content: str
    created_at: datetime
    likes_count: int
    dislikes_count: int
    parent_id: Optional[UUID] = None
    video_id: UUID
    video_title: str

    model_config = ConfigDict(from_attributes=True)


class OwnerCommentPage(Page[OwnerCommentRead]):
    """Paginated list of comments-on-my-videos."""

    pass


def to_owner_comment_read(c: Comment) -> OwnerCommentRead:
    return OwnerCommentRead(
        id=c.id,
        user_id=c.user_id,
        user_name=getattr(c.user, "name", "Anonymous"),
        user_avatar=getattr(c.user, "avatar_url", None),
        content=c.content,
        created_at=c.created_at,
        likes_count=c.likes_count,
        dislikes_count=c.dislikes_count,
        parent_id=c.parent_id,
        video_id=c.video_id,
        video_title=getattr(c.video, "name", "(unknown)"),
    )


class CommentCreateRequest(BaseModel):
    content: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="The text content of the comment.",
    )
    parent_id: Optional[UUID] = Field(
        default=None,
        description="Optional ID of the parent comment if this is a reply.",
    )

    @field_validator("content")
    @classmethod
    def content_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Comment content cannot be empty or just whitespace.")
        return v.strip()
