import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List

from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..infrastructure.database import Base

if TYPE_CHECKING:
    from .comments import Comment
    from .playlist import Playlist
    from .video import Video
    from .video_reactions import VideoReaction
    from .video_views import VideoView


class User(Base):
    __tablename__ = "users"

    # ---- Columns ----
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    username: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    registered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # ---- Relationships ----
    videos: Mapped[List["Video"]] = relationship(back_populates="owner")
    playlists: Mapped[List["Playlist"]] = relationship(back_populates="owner")
    comments: Mapped[List["Comment"]] = relationship(back_populates="user")
    reactions: Mapped[List["VideoReaction"]] = relationship(back_populates="user")

    # Likes only (filtered view of reactions)
    likes: Mapped[List["VideoReaction"]] = relationship(
        back_populates="user",
        viewonly=True,
    )

    views: Mapped[List["VideoView"]] = relationship(back_populates="user")
