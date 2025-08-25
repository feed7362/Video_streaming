from sqlalchemy.dialects.postgresql import UUID
import uuid
from sqlalchemy.orm import relationship
from ..services.database import Base
from sqlalchemy import (
    Column, String, DateTime, ForeignKey, func
)


class HLSFile(Base):
    __tablename__ = "hls_files"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    video_id = Column(UUID(as_uuid=True), ForeignKey("videos.id"), nullable=False)
    resolution = Column(String, nullable=False)  # e.g., 360p, 720p
    url = Column(String, nullable=False)  # S3/MinIO or local path
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    video = relationship("Video", back_populates="hls_files")
