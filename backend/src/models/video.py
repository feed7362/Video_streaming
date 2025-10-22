import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List

from sqlalchemy import Boolean, DateTime, Enum, Float, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..infrastructure.database import Base
from ..schemas.enum import Privacy, VideoStatus

if TYPE_CHECKING:
    from .comments import Comment
    from .hls_files import HLSFile
    from .playlist import Playlist
    from .user import User
    from .video_reactions import VideoReaction
    from .video_views import VideoView


class Video(Base):
    __tablename__ = "videos"

    # ---- Columns ----
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    size: Mapped[float] = mapped_column(Float, nullable=False)
    hash: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    privacy: Mapped[Privacy] = mapped_column(Enum(Privacy), default=Privacy.PUBLIC)
    status: Mapped[VideoStatus] = mapped_column(
        Enum(VideoStatus), default=VideoStatus.PROCESSING
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # ---- Relationships ----
    owner: Mapped["User"] = relationship(back_populates="videos")
    hls_files: Mapped[List["HLSFile"]] = relationship(back_populates="video")
    comments: Mapped[List["Comment"]] = relationship(back_populates="video")
    reactions: Mapped[List["VideoReaction"]] = relationship(back_populates="video")
    views: Mapped[List["VideoView"]] = relationship(back_populates="video")

    playlists: Mapped[List["Playlist"]] = relationship(
        "Playlist",
        secondary="playlist_video",
        back_populates="videos",
    )
