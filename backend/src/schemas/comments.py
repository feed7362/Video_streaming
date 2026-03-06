from datetime import datetime
from typing import Generic, List, Optional, TypeVar
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

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

    model_config = ConfigDict(from_attributes=True)


def to_comment_read(c: Comment) -> CommentRead:
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
    )


class Page(BaseModel, Generic[T]):
    items: List[T]
    page: int
    size: int
    total: int


class CommentPage(Page[CommentRead]):
    """Paginated list of comments."""

    pass


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
