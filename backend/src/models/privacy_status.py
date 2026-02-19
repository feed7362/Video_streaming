import uuid
from typing import TYPE_CHECKING, List

from sqlalchemy import UUID, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure import Base

if TYPE_CHECKING:
    from video import Video


class PrivacyStatus(Base):
    __tablename__ = "privacy_statuses"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)

    videos: Mapped[List["Video"]] = relationship(back_populates="privacy")
