from sqlalchemy.dialects.postgresql import UUID
import uuid
from sqlalchemy.orm import relationship
from ..schemas.video import Privacy, VideoStatus
from ..services.database import Base
from sqlalchemy import (
    Column, String, DateTime, Boolean, Float, ForeignKey, Text, Enum, func
)


class Video(Base):
    __tablename__ = "videos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    description = Column(Text)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    size = Column(Float, nullable=False)
    hash = Column(String, unique=True, nullable=False)
    is_verified = Column(Boolean, default=False)
    privacy = Column(Enum(Privacy), default=Privacy.PUBLIC)
    status = Column(Enum(VideoStatus), default=VideoStatus.PROCESSING)
    registered_at = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User", back_populates="videos")
    hls_files = relationship("HLSFile", back_populates="video")
    comments = relationship("Comment", back_populates="video")
    likes = relationship("VideoLike", back_populates="video")
    views = relationship("VideoView", back_populates="video")