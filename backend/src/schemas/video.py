from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from .enum import Privacy, VideoStatus


class VideoBase(BaseModel):
    name: str
    description: Optional[str] = None
    size: float
    privacy: Privacy = Privacy.PUBLIC


class VideoCreate(VideoBase):
    hash: str


class VideoRead(VideoBase):
    id: UUID
    user_id: UUID
    is_verified: bool
    status: VideoStatus
    registered_at: datetime

    class Config:
        from_attributes = True


class VideoInfo(VideoRead):
    thumbnail_url: Optional[str] = None
    avatar_poster_url: Optional[str] = None
