from datetime import datetime
from typing import TYPE_CHECKING, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from video import VideoRead


class PlaylistBase(BaseModel):
    name: str
    description: Optional[str] = None


class PlaylistCreate(PlaylistBase):
    """Schema for creating a new playlist."""

    pass


class PlaylistRead(PlaylistBase):
    """Schema for reading a playlist (response model)."""

    id: UUID
    user_id: UUID
    created_at: datetime

    # Field(default_factory=...) to avoid mutable default (important!)
    videos: List["VideoRead"] = Field(default_factory=list)

    class Config:
        from_attributes = True
