import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Index, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from ..infrastructure.database import Base

if TYPE_CHECKING:
    from .user import User
    from .video import Video


class Comment(Base):
    __tablename__ = "comments"

    # ---- Columns ----
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    video_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("videos.id"), nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # ---- Relationships ----
    video: Mapped["Video"] = relationship(back_populates="comments")
    user: Mapped["User"] = relationship(back_populates="comments")

    __table_args__ = (
        Index("ix_comments_video_id", "video_id"),
        Index("ix_comments_user_id", "user_id"),
    )

    @validates("content")
    def validate_content(self, _, value: str) -> str:
        assert value.strip(), "Comment cannot be empty"
        return value.strip()

    def __repr__(self):
        return f"<Comment {self.id} by {self.user_id}>"

    def __str__(self):
        return f"Comment by {self.user_id} on video {self.video_id}"
