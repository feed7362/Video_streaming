from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel
from video import VideoRead


class PlaylistBase(BaseModel):
    name: str
    description: Optional[str] = None


class PlaylistCreate(PlaylistBase):
    pass


class PlaylistRead(PlaylistBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    videos: List["VideoRead"] = []

    class Config:
        from_attributes = True
