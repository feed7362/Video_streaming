import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List
from uuid import NAMESPACE_DNS, uuid5

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from ..infrastructure.database import Base

if TYPE_CHECKING:
    from .category import Category
    from .channel import Channel
    from .comments import Comment
    from .playlist import Playlist
    from .privacy_status import PrivacyStatus
    from .video_reactions import VideoReaction
    from .video_resolutions import VideoResolution
    from .video_status import VideoStatus
    from .video_views import VideoView
    from .watch_history import WatchHistory
    from .watch_later import WatchLater


class Video(Base):
    __tablename__ = "videos"

    # ---- Columns ----
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    size: Mapped[int] = mapped_column(Integer, nullable=False)
    hash: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    video_path: Mapped[str] = mapped_column(String, nullable=True)
    thumbnail_path: Mapped[str] = mapped_column(String, nullable=True)

    channel_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("channels.id", ondelete="CASCADE"), nullable=False
    )
    views_count: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default="0"
    )
    likes_count: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default="0"
    )
    dislikes_count: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default="0"
    )
    privacy_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("privacy_statuses.id"), nullable=False
    )
    category_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("categories.id"), nullable=False
    )
    status_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("video_statuses.id"),
        default=uuid5(NAMESPACE_DNS, "video_status:processing"),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # ---- Relationships ----
    channel: Mapped["Channel"] = relationship(back_populates="videos")
    status: Mapped["VideoStatus"] = relationship(back_populates="videos")
    category: Mapped["Category"] = relationship(back_populates="videos")
    comments: Mapped[List["Comment"]] = relationship(
        back_populates="video", cascade="all, delete-orphan"
    )
    reactions: Mapped[List["VideoReaction"]] = relationship(
        back_populates="video", cascade="all, delete-orphan"
    )
    views: Mapped[List["VideoView"]] = relationship(
        back_populates="video", cascade="all, delete-orphan"
    )
    watch_history: Mapped[List["WatchHistory"]] = relationship(
        back_populates="video", cascade="all, delete-orphan"
    )

    privacy: Mapped["PrivacyStatus"] = relationship(back_populates="videos")
    playlists: Mapped[List["Playlist"]] = relationship(
        "Playlist",
        secondary="playlist_video",
        back_populates="videos",
    )
    in_watch_later: Mapped[list["WatchLater"]] = relationship(
        back_populates="video", cascade="all, delete-orphan"
    )
    resolutions: Mapped[list["VideoResolution"]] = relationship(
        back_populates="video", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("ix_videos_user_id", "channel_id"),
        Index("ix_videos_created_at", "created_at"),
        Index("ix_videos_privacy", "privacy_id"),
    )

    @validates("name")
    def validate_name(self, _: str, value: str) -> str:
        assert value.strip(), "Video name cannot be empty"
        return value.strip()

    def __repr__(self) -> str:
        return f"<Video name='{self.name}' status={self.status.value}>"

    def __str__(self) -> str:
        return f"{self.name} — {self.status.value}, {self.privacy}"
