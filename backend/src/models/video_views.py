import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Index, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..infrastructure.database import Base

if TYPE_CHECKING:
    from .user import User
    from .video import Video


class VideoView(Base):
    __tablename__ = "video_views"

    # ---- Columns ----
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    video_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("videos.id"), nullable=False
    )
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    viewed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # ---- Relationships ----
    video: Mapped["Video"] = relationship(back_populates="views")
    user: Mapped["User | None"] = relationship(back_populates="views")

    __table_args__ = (
        Index("ix_video_views_video_id", "video_id"),
        Index("ix_video_views_user_id", "user_id"),
    )

    def __repr__(self):
        return f"<View video={self.video_id} user={self.user_id}>"

    def __str__(self):
        return f"View of {self.video_id} by {self.user_id or 'guest'}"
