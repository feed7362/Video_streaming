import uuid
from datetime import datetime
from enum import StrEnum
from typing import TYPE_CHECKING, List

from sqlalchemy import Boolean, DateTime, Enum, Index, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from ..infrastructure.database import Base

if TYPE_CHECKING:
    from .comments import Comment
    from .playlist import Playlist
    from .video import Video
    from .video_reactions import VideoReaction
    from .video_views import VideoView


class UserRole(StrEnum):
    ADMIN = "admin"
    CREATOR = "creator"
    VIEWER = "viewer"


class User(Base):
    __tablename__ = "users"

    # ---- Columns ----
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    username: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="user_role_enum"), default=UserRole.VIEWER
    )
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    registered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # ---- Relationships ----
    videos: Mapped[List["Video"]] = relationship(
        back_populates="owner", cascade="all, delete-orphan"
    )
    playlists: Mapped[List["Playlist"]] = relationship(
        back_populates="owner", cascade="all, delete-orphan"
    )
    comments: Mapped[List["Comment"]] = relationship(back_populates="user")
    reactions: Mapped[List["VideoReaction"]] = relationship(back_populates="user")
    views: Mapped[List["VideoView"]] = relationship(back_populates="user")

    __table_args__ = (
        Index("ix_users_email", "email"),
        Index("ix_users_username", "username"),
    )

    @validates("email")
    def validate_email(self, _, value):
        assert "@" in value, "Invalid email address"
        return value

    def __repr__(self) -> str:
        return (
            f"User(id={self.id!r}, name={self.username!r}, email={self.email!r}, role={self.role!r}"
            f" is_active={self.is_active!r}, is_verified={self.is_verified!r}, "
            f"registered_at={self.registered_at!r})"
        )

    def __str__(self) -> str:
        return (
            f"{self.username} ({self.email}) — "
            f"{'Active' if self.is_active else 'Inactive'},"
            f"{'Verified' if self.is_verified else 'Unverified'},"
            f"Role: {self.role},"
            f"Register at{self.registered_at}."
        )
