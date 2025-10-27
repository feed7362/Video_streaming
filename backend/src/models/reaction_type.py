import uuid

from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..infrastructure.database import Base


class ReactionType(Base):
    __tablename__ = "reaction_types"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    path: Mapped[str] = mapped_column(String, nullable=True)
    video_reactions = relationship("VideoReaction", back_populates="reaction_type")
    comment_reactions = relationship("CommentReaction", back_populates="reaction_type")
