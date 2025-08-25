from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import datetime


class PlaylistBase(BaseModel):
    name: str
    description: Optional[str] = None


class PlaylistCreate(PlaylistBase):
    pass


class PlaylistRead(PlaylistBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    videos: List['VideoRead'] = []

    class Config:
        from_attributes = True
