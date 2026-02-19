import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Column, DateTime, ForeignKey, Index, String, Table, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from src.infrastructure.database import Base

if TYPE_CHECKING:
    from user import User
    from video import Video


# --- Association table (many-to-many) ---
playlist_video = Table(
    "playlist_video",
    Base.metadata,
    Column(
        "playlist_id",
        UUID(as_uuid=True),
        ForeignKey("playlists.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "video_id",
        UUID(as_uuid=True),
        ForeignKey("videos.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


# --- ORM model ---
class Playlist(Base):
    __tablename__ = "playlists"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    user: Mapped["User"] = relationship(back_populates="playlists")
    videos: Mapped[list["Video"]] = relationship(
        "Video",
        secondary=playlist_video,
        back_populates="playlists",
        cascade="all",
    )

    __table_args__ = (
        Index("ix_playlists_user_id", "user_id"),
        Index("ix_playlists_created_at", "created_at"),
    )

    @validates("name")
    def validate_name(self, _: str, value: str) -> str:
        assert value.strip(), "Playlist name cannot be empty"
        return value.strip()

    def __repr__(self) -> str:
        return f"<Playlist {self.name} ({len(self.videos)} videos)>"

    def __str__(self) -> str:
        return f"Playlist: {self.name}"
