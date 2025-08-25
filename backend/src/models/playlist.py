from sqlalchemy.dialects.postgresql import UUID
import uuid
from sqlalchemy.orm import relationship
from ..services.database import Base
from sqlalchemy import (
    Column, String, DateTime, Table, Text, ForeignKey, func
)

playlist_video = Table(
    "playlist_video", Base.metadata,
    Column("playlist_id", UUID(as_uuid=True), ForeignKey("playlists.id")),
    Column("video_id", UUID(as_uuid=True), ForeignKey("videos.id"))
)


class Playlist(Base):
    __tablename__ = "playlists"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    description = Column(Text)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User", back_populates="playlists")
    videos = relationship("Video", secondary=playlist_video, backref="playlists")
