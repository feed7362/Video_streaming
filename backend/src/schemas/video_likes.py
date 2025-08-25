from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class VideoLikeBase(BaseModel):
    is_like: bool


class VideoLikeCreate(VideoLikeBase):
    video_id: UUID


class VideoLikeRead(VideoLikeBase):
    id: UUID
    video_id: UUID
    user_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True
