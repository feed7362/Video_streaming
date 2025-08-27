import uuid

from sqlalchemy import Column, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from ..services.database import Base


class VideoView(Base):
    __tablename__ = "video_views"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    video_id = Column(UUID(as_uuid=True), ForeignKey("videos.id"), nullable=False)
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )  # guest views = NULL
    viewed_at = Column(DateTime(timezone=True), server_default=func.now())

    video = relationship("Video", back_populates="views")
    user = relationship("User", back_populates="views")
