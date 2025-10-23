import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Index, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from ..infrastructure.database import Base

if TYPE_CHECKING:
    from .video import Video


class HLSFile(Base):
    __tablename__ = "hls_files"

    # ---- Columns ----
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    video_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("videos.id"), nullable=False
    )
    resolution: Mapped[str] = mapped_column(String, nullable=False)  # e.g. 360p, 720p
    url: Mapped[str] = mapped_column(String, nullable=False)  # S3/MinIO or local path
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # ---- Relationships ----
    video: Mapped["Video"] = relationship(back_populates="hls_files")

    __table_args__ = (
        Index("ix_hls_files_video_id", "video_id"),
        Index("ix_hls_files_resolution", "resolution"),
    )

    @validates("resolution")
    def validate_resolution(self, _, value: str) -> str:
        assert value.endswith("p"), "Resolution must end with 'p' (e.g., 720p)"
        return value

    def __repr__(self):
        return f"<HLSFile {self.resolution} for video {self.video_id}>"

    def __str__(self):
        return f"{self.resolution} stream — {self.url}"
