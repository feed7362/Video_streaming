import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.database import Base

if TYPE_CHECKING:
    from reaction_type import ReactionType
    from user import User
    from video import Video


class VideoReaction(Base):
    __tablename__ = "video_reactions"
    __table_args__ = (UniqueConstraint("user_id", "video_id"),)

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    video_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("videos.id", ondelete="CASCADE"), nullable=False
    )
    reaction_type_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("reaction_types.id", ondelete="CASCADE"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    user: Mapped["User"] = relationship(back_populates="video_reactions")
    video: Mapped["Video"] = relationship(back_populates="reactions")
    reaction_type: Mapped["ReactionType"] = relationship(
        back_populates="video_reactions"
    )
