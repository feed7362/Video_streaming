import uuid
from typing import TYPE_CHECKING, List

from sqlalchemy import String
from sqlalchemy.dialects.postgresql.base import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..infrastructure.database import Base

if TYPE_CHECKING:
    from .video import Video


class VideoStatus(Base):
    __tablename__ = "video_statuses"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    value: Mapped[str] = mapped_column(String, nullable=False, unique=True)

    videos: Mapped[List["Video"]] = relationship(back_populates="status")
