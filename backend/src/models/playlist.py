import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List

from sqlalchemy import Column, DateTime, ForeignKey, String, Table, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..infrastructure.database import Base

if TYPE_CHECKING:
    from .user import User
    from .video import Video


# --- Association table (many-to-many) ---
playlist_video = Table(
    "playlist_video",
    Base.metadata,
    Column("playlist_id", UUID(as_uuid=True), ForeignKey("playlists.id")),
    Column("video_id", UUID(as_uuid=True), ForeignKey("videos.id")),
)


# --- ORM model ---
class Playlist(Base):
    __tablename__ = "playlists"

    # ---- Columns ----
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # ---- Relationships ----
    owner: Mapped["User"] = relationship(back_populates="playlists")
    videos: Mapped[List["Video"]] = relationship(
        "Video", secondary=playlist_video, back_populates="playlists"
    )
