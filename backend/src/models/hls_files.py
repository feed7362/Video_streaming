import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

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
