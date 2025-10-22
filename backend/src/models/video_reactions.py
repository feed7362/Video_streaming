import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..infrastructure.database import Base

if TYPE_CHECKING:
    from .user import User
    from .video import Video


class VideoReaction(Base):
    __tablename__ = "video_reactions"

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
    is_like: Mapped[bool] = mapped_column(
        Boolean, nullable=False
    )  # True = like, False = dislike
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # ---- Relationships ----
    video: Mapped["Video"] = relationship(back_populates="reactions")
    user: Mapped["User"] = relationship(back_populates="likes")
