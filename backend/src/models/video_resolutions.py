import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Index, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.database import Base

if TYPE_CHECKING:
    from video import Video


class VideoResolution(Base):
    __tablename__ = "video_resolutions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    video_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("videos.id", ondelete="CASCADE"), nullable=False
    )

    height: Mapped[int] = mapped_column(Integer, nullable=False)
    width: Mapped[int] = mapped_column(Integer, nullable=False)
    bitrate: Mapped[int] = mapped_column(Integer, nullable=False)  # kbps
    playlist_path: Mapped[str] = mapped_column(String, nullable=False)

    video: Mapped["Video"] = relationship(back_populates="resolutions")

    __table_args__ = (Index("ix_video_resolutions_video_id", "video_id"),)
