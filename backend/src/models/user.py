from sqlalchemy.dialects.postgresql import UUID
import uuid
from sqlalchemy.orm import relationship
from ..services.database import Base
from sqlalchemy import (
    Column, String, DateTime, Boolean, func
)


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    registered_at = Column(DateTime(timezone=True), server_default=func.now())

    videos = relationship("Video", back_populates="owner")
    playlists = relationship("Playlist", back_populates="owner")
    comments = relationship("Comment", back_populates="user")
    likes = relationship("VideoLike", back_populates="user")
    views = relationship("VideoView", back_populates="user")
