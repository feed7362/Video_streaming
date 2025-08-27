import uuid

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from ..services.database import Base


class VideoLike(Base):
    __tablename__ = "video_likes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    video_id = Column(UUID(as_uuid=True), ForeignKey("videos.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    is_like = Column(Boolean, nullable=False)  # True=like, False=dislike
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    video = relationship("Video", back_populates="likes")
    user = relationship("User", back_populates="likes")
