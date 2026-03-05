import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.database import Base

if TYPE_CHECKING:
    from channel import Channel
    from comment_reactions import CommentReaction
    from comments import Comment
    from notification import Notification
    from playlist import Playlist
    from subscription import Subscription
    from user_roles import Role
    from user_status import UserStatus
    from video_reactions import VideoReaction
    from video_views import VideoView
    from watch_history import WatchHistory
    from watch_later import WatchLater


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    username: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    hash_password: Mapped[str] = mapped_column(String, nullable=False)
    status_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("user_statuses.id", ondelete="SET NULL"),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=func.now()
    )
    role_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("roles.id", ondelete="SET NULL"), nullable=True
    )
    status: Mapped["UserStatus"] = relationship(back_populates="users")
    channels: Mapped[List["Channel"]] = relationship(
        back_populates="user", cascade="all, delete"
    )
    role: Mapped["Role"] = relationship(back_populates="users")
    comments: Mapped[List["Comment"]] = relationship(back_populates="user")
    video_reactions: Mapped[List["VideoReaction"]] = relationship(back_populates="user")
    comment_reactions: Mapped[List["CommentReaction"]] = relationship(
        back_populates="user"
    )
    views: Mapped[List["VideoView"]] = relationship(back_populates="user")
    playlists: Mapped[List["Playlist"]] = relationship(back_populates="user")
    subscriptions: Mapped[List["Subscription"]] = relationship(
        back_populates="subscriber"
    )
    notifications: Mapped[List["Notification"]] = relationship(back_populates="user")
    watch_history: Mapped[List["WatchHistory"]] = relationship(back_populates="user")
    watch_later: Mapped[list["WatchLater"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
