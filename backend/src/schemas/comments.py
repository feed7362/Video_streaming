from datetime import datetime
from typing import Generic, List, Optional, TypeVar
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from ..models import Comment

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
