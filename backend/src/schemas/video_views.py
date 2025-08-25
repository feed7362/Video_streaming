from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime


class VideoViewBase(BaseModel):
    pass


class VideoViewCreate(VideoViewBase):
    video_id: UUID


class VideoViewRead(VideoViewBase):
    id: UUID
    video_id: UUID
    user_id: Optional[UUID]
    viewed_at: datetime

    class Config:
        from_attributes = True
